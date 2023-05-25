import unittest
import click
from pr_duration.cli import get_closed_pull_requests


class GithubPullRequestsTestCase(unittest.TestCase):
    def test_get_prs(self):
        results = get_closed_pull_requests("django/django", token=None, max_prs=101)
        self.assertEqual(len(results), 200)

    def test_private_repo(self):
        with self.assertRaises(click.Abort):
            get_closed_pull_requests("sesh/private", token=None, max_prs=100)
