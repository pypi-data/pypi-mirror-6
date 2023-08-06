Launchpad show my bugs
======================

Console utility that displays your current bug list from Launchpad.net

How to use
==========

# Installation

Using pip

```shell
$ pip install lp-show-my-bugs
```
Using pip + github
```shell
$ pip install git+https://github.com/niedbalski/lp-show-my-bugs
```

# Usage

## Using the ClI

Basic usage:

```bash
$ lp-show-my-bugs --author="niedbalski" --project="any-project" --sort_by="date_created:asc"
```

Limiting results:
```bash
$ lp-show-my-bugs --author="niedbalski" --project="any-project" --sort_by="date_created:asc --limit=10"
```

The output will looks like:

![Output](https://raw.github.com/niedbalski/lp-show-my-bugs/master/images/output.png)


## Programmatically

```python
from lp_show_my_bugs import LaunchpadShowMyBugs

#specify the author
lp = LaunchpadShowMyBugs('niedbalski')

#add filters, (multiple supported)
lp.add_filter('bug_target_name', 'any-project')

#sort by date_created in descending order
lp.sort_by('date_created', 'desc')

#fetch the assigned bugs
bugs = lp.fetch()

for bug in bugs:
    print bug.date_created, bug.title
```
=======
lp-show-my-bugs
===============

Console client for displaying your Launchpad.net bugs
