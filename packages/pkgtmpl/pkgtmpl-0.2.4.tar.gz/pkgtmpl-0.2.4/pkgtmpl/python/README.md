# {{ appname }}

[![PyPI version](https://pypip.in/v/{{ appname }}/badge.png)](https://pypi.python.org/pypi/{{ appname }})
[![PyPI downloads](https://pypip.in/d/{{ appname }}/badge.png)](https://pypi.python.org/pypi/{{ appname }})
{% if travis_ci %}[![Build Status]({{ travis_ci.url }}.png?branch={{ travis_ci.branch }})](travis_ci.url){% endif %}

Created by {% if twitter %}[{{ full_name }}](https://twitter.com/{{ twitter }}){% else %}{{ full_name }}{% endif %}, {{ year }}. Full list of contributors can be found in [CONTRIBUTORS.md](blob/master/CONTRIBUTING.md).


## About

TODO: Write


## Installation

Install using `pip`...

    pip install {{ appname }}

...or clone the project from github.

    git clone https://github.com/{{ github_username }}/{{ appname }}.git


## Documentation
[docs]


[docs]: https://github.com/{{ github_username }}/{{ appname }}
