**Author:** Jacob Magnusson. [Follow me on Twitter](twitter)

## About

Bootstrap python packages with sane defaults

Features include:

* Generates .gitignore, AUTHORS, CHANGELOG,
  LICENSE (BSD simplified by default), MANIFEST.in, README.md,
  requirements.txt, setup.py, tests.py and tox.ini.
* Sets your name, github username, package name in the templates by
  reading a config that should be located @ ~/.config/pkgtmpl.ini.
* Optional: Add Travis CI status and twitter account to the readme
* Sets your name and year in the copyright notice of the license file


## Installation

    $ pip install pkgtmpl


## Usage

Create `~/.config/pkgtmpl.ini` with your details. Example contents:

    [general]
    full_name = Jacob Magnusson
    email = m@jacobian.se
    github_username = jmagnusson
    twitter = pyjacob

Basic usage example:

    $ pkgtmpl mypackage ~/apps/mypackage

For more options:

    $ pkgtmpl --help


## Python support

Python 2.7+ and Python 3.3+.


## Documentation
[docs]


[twitter]: https://twitter.com/pyjacob
[docs]: https://github.com/jmagnusson/pkgtmpl
