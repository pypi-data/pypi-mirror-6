#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jorge Niedbalski R. <jnr@metaklass.org>'

from launchpadlib.launchpad import Launchpad

import os


class LaunchpadShowMyBugs(object):

    CACHE_DIRECTORY = os.path.expanduser('~/.launchpadlib/cache')

    def __init__(self, author):
        self.author = author
        self.launchpad = Launchpad.login_with(
            'hello-world', 'production', self.CACHE_DIRECTORY)
        self.filters = {}

    def add_filter(self, name, value):
        if not name in self.filters.keys():
            self.filters[name] = []
        self.filters[name].append(value)

    def apply_filters(self, task):
        r = []
        for f, v in self.filters.items():
            if hasattr(task, f):
                for vv in v:
                    r.append(getattr(task, f) == vv)
        return any(r)

    @classmethod
    def format_date_created(cls, value):
        return value.strftime("%m/%d/%Y")

    @classmethod
    def hydrate_bug(cls, bug, attributes):
        ret = {}
        for attribute in attributes:
            attr = getattr(bug, attribute)
            if hasattr(cls, 'format_%s' % attribute):
                attr = getattr(cls, 'format_%s' % attribute)(attr)
            ret[attribute] = attr
        return ret

    def sort_by(self, name, kind):
        (self.sort_by, self.sort_direction) = (name, kind)

    def apply_sort(self, tasks):
        reverse = False
        if self.sort_direction == 'desc':
            reverse = True
        tasks.sort(key=lambda x: getattr(x, self.sort_by),
                   reverse=reverse)
        return tasks

    def _fetch_tasks(self):
        tasks = self.launchpad.people[self.author].searchTasks()
        ret = []
        for task in tasks:
            if self.apply_filters(task):
                ret.append(task)
        return ret

    def fetch(self, limit=None):
        tasks = self.apply_sort(self._fetch_tasks())
        if limit:
            return tasks[0:limit]
        return tasks
