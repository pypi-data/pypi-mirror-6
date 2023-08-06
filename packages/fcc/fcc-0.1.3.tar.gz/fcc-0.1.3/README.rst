=======
fcc-api
=======

A pleasant interface for the United States Federal Communications Commission (FCC) data transparency services.

Other Work
==========

Sure, there's <https://github.com/codeforamerica/FCC-Python-Egg>, but I'm not a fan of the name and it hasn't been updated in a couple years (as of 2014-Mar-12).

Installation
============

Like most other PyPI packages. ::

    pip install fcc

Or download the source code and run `setup.py` ::

    python setup.py install


Usage
=====

Import the wrapper functions to use in your code. ::

    >>> from fcc.census_block_conversions import census_block_fips
    >>> census_block_fips(34.86,-111.79)
    '040250018012017'

Or use the simple command line script. ::

    $ census_block_conversions 34.86 -111.79
    040250018012017
    $ echo '34.86,-111.79' > coordinates.csv
    $ census_block_conversions < coordinates.csv
    040250018012017
