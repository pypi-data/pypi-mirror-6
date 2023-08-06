****************
Photometric Data
****************

Quick start
===========

For an example of an acceptable photometric data representation, you can do::

    >>> data = sncosmo.load_example_data()

``data`` is an astropy `~astropy.table.table.Table`
representing a table of photometric observations. For a pretty-printed
version of this, you can do::

    >>> print data
         time      band        flux          fluxerr      zp  zpsys
    ------------- ----- ----------------- -------------- ---- -----
          55070.0 sdssg    0.813499900062 0.651728140824 25.0    ab
    55072.0512821 sdssr  -0.0852238865812 0.651728140824 25.0    ab
    55074.1025641 sdssi -0.00681659003089 0.651728140824 25.0    ab
    55076.1538462 sdssz     2.23929135407 0.651728140824 25.0    ab
    55078.2051282 sdssg  -0.0308977349373 0.651728140824 25.0    ab
    55080.2564103 sdssr     2.35450321853 0.651728140824 25.0    ab
    ...

It has metadata stored in ``data.meta`` as an `OrderedDict`.

Photometric Data: Structure
===========================

Usually, photometric data can naturally be represented as a table of
observations. Rather than imposing a new, unfamiliar format or class for
representing such data, the approach taken in sncosmo is to use astropy `~astropy.table.table.Table` objects.

Whichever structure is used, the data must have certain recognizable
columns. For photometric data with Gaussian uncertainties in
flux-space (often a good approximation), the following quantities
uniquely specify a single observation:

* The time of the observation (e.g., MJD, etc)
* The bandpass in which the observation was taken
* The flux
* The uncertainty on the flux
* The zeropoint tying the flux to a physical system.
* The magnitude system that the zeropoint is in.

Therefore, ``data`` must have a column to represent each quantity. The
column *names* are somewhat flexible. The table below shows the
acceptable column names for ``data``. For example ``data`` must
contain exactly one of ``'date'``, ``'jd'``, ``'mjdobs'``, ``'mjd'``,
or ``'time'``.

.. automodule:: sncosmo.photdata

Reading and Writing photometric data from files
===============================================

SNCosmo strives to be agnostic with respect to file format. In
practice there are a plethora of different file formats, both standard
and non-standard, used to represent tables. Rather than picking a
single supported file format, or worse, creating yet another new
"standard", we choose to leave the file format mostly up to the user:
It is the user's job to read their data into an `~astropy.table.table.Table`.

That said, SNCosmo does include a couple convenience functions for
reading and writing tables of photometric data: `sncosmo.read_lc` and
`sncosmo.write_lc`.

The supported formats are listed below. If your preferred format is
not available, write your own parser or use a standard one from the
python universe.

+-------------+-----------------------------+-------------------------------+
| Format name | Description                 | Notes                         |
+=============+=============================+===============================+
| ascii       | ASCII with metadata         | Not readable by               |
|             | lines marked by '@'         | standard ASCII table parsers  |
+-------------+-----------------------------+-------------------------------+
| json        | JavaScript Object Notation  | Good performance, but not as  |
|             |                             | human-readable as ascii       |
+-------------+-----------------------------+-------------------------------+
| salt2       | SALT2 new-style data files  | Mostly untested.              |
+-------------+-----------------------------+-------------------------------+
| salt2-old   | SALT2 old-style data files  | Mostly untested.              |
+-------------+-----------------------------+-------------------------------+

To see what each format looks like, you can do, e.g.::

    >>> data = sncosmo.load_example_data()
    >>> sncosmo.write_lc(data, fname='test.json', format='json')


Manipulating data tables
========================

Rename a column::

    >>> data.rename_column('oldname', 'newname')

Add a column::

    >>> data['zp'] = 26.

Add a constant value to all the entries in a given column::

    >>> data['zp'] += 0.03
