import os

from setuptools import setup

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="pr-duration",
    description="PR Open -> PR Merged",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/sesh/pr-duration",
    project_urls={
        "Issues": "https://github.com/sesh/pr-duration/issues",
        "CI": "https://github.com/sesh/pr-duration/actions",
        "Changelog": "https://github.com/sesh/pr-duration/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["pr_duration"],
    entry_points="""
        [console_scripts]
        pr-duration=pr_duration.cli:cli
    """,
    install_requires=["click", "thttp"],
    extras_require={"test": ["coverage"]},
    python_requires=">=3.7",
)
