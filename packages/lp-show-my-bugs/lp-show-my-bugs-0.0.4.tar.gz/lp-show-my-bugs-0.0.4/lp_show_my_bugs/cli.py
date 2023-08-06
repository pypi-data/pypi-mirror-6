#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jorge Niedbalski R. <jnr@metaklass.org>'

import argparse

from lp_show_my_bugs import LaunchpadShowMyBugs
from tabulate import tabulate


def print_bugs(lp, bugs, attributes=('status', 'date_created', 'web_link',
                                     'title', )):
    to_print = []
    for bug in bugs:
        to_print.append(LaunchpadShowMyBugs.hydrate_bug(bug,
                                                        attributes).values())
    print tabulate(to_print, attributes, tablefmt="grid")


def parse_options():
    parser = argparse.ArgumentParser(description=
                'A tool for fetching all your associated bugs on launchpad')

    parser.add_argument("--limit",
                        default=None,
                        help='Max amount of results to show',
                        type=int,
                        metavar='limit')

    parser.add_argument("--author",
                        help='Specify the launchpad username',
                        type=str,
                        required=True,
                        metavar='author')

    parser.add_argument("--sort_by",
                        default="date_created:desc",
                        type=str,
                        metavar='sort_by')

    parser.add_argument("--project",
                        type=str,
                        required=True,
                        metavar='project')

    args = parser.parse_args()
    return args


def main():
    options = parse_options()

    lp = LaunchpadShowMyBugs(options.author)
    lp.add_filter('bug_target_name', options.project)

    (sort_by, sort_kind) = options.sort_by.split(":")
    lp.sort_by(sort_by, sort_kind)

    print_bugs(lp, lp.fetch(limit=options.limit))


if __name__ == '__main__':
    main()
