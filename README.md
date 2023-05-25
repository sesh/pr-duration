# pr-duration

Check in on how long it takes your Pull Requests to go from Open -> Merged.

## Installation

Install this tool using `pip`:

    pip install pr-duration

## Usage

By default the tool will output the average and median duration that PRs merged in the last 30 days were open for.
Provide the `--repo` argument to output the average duration for a single repo:

    pr-duration --token=<github-pat> --repo=sesh/pr-duration

Use `--token` with a Github token that has the correct access if you are checking a private repo:

    pr-duration --token=<github-pat> --repo=sesh/private

For help and details of other options, run:

    pr-duration --help

You can also use:

    python -m pr_duration --help


## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd pr-duration
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'
