# Pycalenvite: Easy way to handle your invitations

[![Show Travis Build Status](https://travis-ci.org/guyzmo/pycalenvite.svg)](https://travis-ci.org/guyzmo/pycalenvite)
[![Code Climate](https://codeclimate.com/github/guyzmo/pycalenvite/badges/gpa.svg)](https://codeclimate.com/github/guyzmo/pycalenvite)
[![Test Coverage](https://codeclimate.com/github/guyzmo/pycalenvite/badges/coverage.svg)](https://codeclimate.com/github/guyzmo/pycalenvite/coverage)

This tool enables you to send invites for a meeting, leaving your mate choose the
time/date of his preference, given your availabilities.

## Development

Either you can use buildout:

    % buildout
    % bin/py.test

Or you can use nothing:

    % python3 setup.py test

Or you can use your favorite *env thing.

## TODO

* Make it support reccurent events (ics.py)
* Make it support event arithmetics (PR waiting in ics.py)
* For tests, support of class-wide datadir (PR waiting in datadir)
* Adapt the code so it's convenient to the UI (webpack integration?)

Notes:

 * While PRs are pending, a hard dependencies are made to forks of ics.py and
   datadir, check requirements.txt (and buildout.cfg) for which.

## Usage

    % buildout
    % bin/calenvite --verbose

or run calenvite from your favorite *env thing.

## License

GPL

