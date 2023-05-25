from datetime import datetime, timedelta, timezone

import click
from thttp import request


class PR:
    def __init__(self, j):
        self._json = j

    def author(self):
        return self._json["user"]["login"]

    def open_duration(self):
        if self._json["merged_at"]:
            return (
                datetime.fromisoformat(self._json["merged_at"]) - datetime.fromisoformat(self._json["created_at"])
            ).total_seconds()

    def is_merged(self):
        return self._json["merged_at"] is not None

    def merged_ago(self):
        """number of days since this was merged"""
        if self._json["merged_at"]:
            return (
                datetime.utcnow().replace(tzinfo=timezone.utc) - datetime.fromisoformat(self._json["merged_at"])
            ).days

    def merged_at(self):
        if self._json["merged_at"]:
            return datetime.fromisoformat(self._json["merged_at"])


def pretty_time_delta(seconds):
    # https://gist.github.com/thatalextaylor/7408395
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return "%dd%dh%dm%ds" % (days, hours, minutes, seconds)
    elif hours > 0:
        return "%dh%dm%ds" % (hours, minutes, seconds)
    elif minutes > 0:
        return "%dm%ds" % (minutes, seconds)
    else:
        return "%ds" % (seconds,)


def get_closed_pull_requests(repo, token, *, max_prs=500):
    print("Max PRs:", max_prs)
    prs = []
    page = 1

    headers = {
        "Accept": "application/vnd.github+json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    while page:
        click.echo(f"Requesting page {page} of PRs from Github ({repo})")

        response = request(
            f"https://api.github.com/repos/{repo}/pulls",
            headers=headers,
            params={
                "state": "closed",
                "per_page": "100",
                "page": page,
            },
        )

        if response.status == 200 and response.json:
            for pr in response.json:
                prs.append(PR(pr))

            page += 1

            if len(prs) >= max_prs:
                return prs
        else:
            return prs

    return prs


@click.group(invoke_without_command=True)
@click.option("--token", help="Github token with repo access (required for private repositories)")
@click.option("--repo", help="Github repository in <org>/<repo> format", required=True)
@click.option(
    "--max-age",
    help="Maximum age of PRs to include in the average, age in days based on merged_at",
    default=30,
)
@click.option("--excluded-authors", help="Comma separated list of authors to exclude")
@click.option("--authors", help="Comma separated list of authors to include")
@click.option("--max-prs", help="The maximum number of PRs to request from Github", default=500)
@click.pass_context
def cli(ctx, token, repo, max_age, excluded_authors, authors, max_prs):
    prs = get_closed_pull_requests(repo, token, max_prs=max_prs)

    click.echo(f"Collected {len(prs)} pull requests from Github")

    # filter: merged
    prs = [pr for pr in prs if pr.is_merged()]
    click.echo(f"Filtered to {len(prs)} that have been merged")

    # filter: max age
    prs = [pr for pr in prs if pr.merged_ago() < max_age]
    click.echo(f"Filtered to {len(prs)} that were merged in the last {max_age} days")

    # filter: excluded authors
    if excluded_authors:
        excluded_authors = [a.strip().lower() for a in excluded_authors.split(",")]
        prs = [pr for pr in prs if pr.author().lower() not in excluded_authors]
        click.echo(f"Filtered to {len(prs)} that were not authored by {excluded_authors}")

    # filter: included authors
    if authors:
        authors = [a.strip().lower() for a in authors.split(",")]
        prs = [pr for pr in prs if pr.author().lower() in authors]
        click.echo(f"Filtered to {len(prs)} that were authored by {authors}")

    ctx.ensure_object(dict)
    ctx.obj["prs"] = prs

    if ctx.invoked_subcommand is None:
        # average time to merge = sum(open_duration) / len(prs)
        total_seconds = sum([pr.open_duration() for pr in prs])
        click.echo(f"Average time to merge: {pretty_time_delta(total_seconds / len(prs))}")

        # median time to merge = the middle PR
        prs = sorted(prs, key=lambda pr: pr.open_duration())
        [pr.open_duration() for pr in prs]
        click.echo(f"Median time to merge: {pretty_time_delta(prs[int(len(prs) / 2)].open_duration())}")


@cli.command(name="graph")
@click.pass_context
def graph(ctx):
    prs = ctx.obj["prs"]
    now = datetime.utcnow().replace(tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    stats_range = 150  # todo: rename / arg
    start = now - timedelta(days=stats_range)  # todo: rename / arg
    window_days = 14  # todo: rename / arg

    # todo: ensure that max-age < start date - window_days

    while start < now:
        in_range = [pr for pr in prs if pr.merged_at() < start and pr.merged_at() > start - timedelta(days=window_days)]

        if in_range:
            total_seconds = sum([pr.open_duration() for pr in in_range])
            avg_dur = total_seconds / len(in_range)
        else:
            avg_dur = 0

        print(f"{start}\t{len(in_range)}\t{int(avg_dur)}\t{pretty_time_delta(avg_dur)}\t{avg_dur / 60 / 60 / 24}")
        start = start + timedelta(days=1)
