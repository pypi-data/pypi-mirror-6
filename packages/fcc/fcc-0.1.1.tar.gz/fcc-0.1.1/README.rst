=======
fcc-api
=======

A pleasant interface for the United States Federal Communications Commission (FCC) data transparency services.

Other Work
==========

Sure, there's <https://github.com/codeforamerica/FCC-Python-Egg>, but I'm not a fan of the name and it hasn't been updated in a couple years (as of 2014-Mar-12).

Installation
============

    python setup.py install


Usage
=====

    >>> import fcc.api as fcc
    >>> fcc.census_block_fips(40,-80)
