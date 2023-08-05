# Changelog

## Version 0.4.0

* Add Python 3 support

## Version 0.03.3

* Include VERSION.txt in pip package

## Version 0.03.2

* Add sphinx documentation
* Add Travis CI support
* Add `list_tables` method to `Table` class
* Make column name/primary key/autoincrement parsing more robust
* Check if SQLite table exists on `Table` initialization
* Allow tests to be run from within `tests` directory

## Version 0.03.1

* Fix `pip install` installation bug

## Version 0.03

* Fix an issue in `Table` initialization from `DataFrame` (#5)
* Allow `Table` initialization from a dictionary of list of
  dictionaries (#2)
* Create testing metaclass to modify test case docstrings to include
  class name
* Add `Makefile` and other minor installation modifications

## Version 0.02

* Add `setup.py` installation support (#4)
* Allow `Table` initialization from a pandas `DataFrame` (#1)
* Fix misues of autoincrement/primary key
* Add `Table.exists` class method

