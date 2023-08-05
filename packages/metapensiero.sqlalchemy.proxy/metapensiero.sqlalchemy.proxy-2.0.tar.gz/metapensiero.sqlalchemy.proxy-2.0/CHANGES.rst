Changes
-------

2.0 (2013-12-23)
~~~~~~~~~~~~~~~~

* The generator function may yield a tuple with modified params and
  other conditions

* Simple Makefile with common recipes


1.9.6 (2013-12-12)
~~~~~~~~~~~~~~~~~~

* Encoding issue on package meta data


1.9.5 (2013-12-12)
~~~~~~~~~~~~~~~~~~

* First official release on PyPI


1.9.4 (2013-12-12)
~~~~~~~~~~~~~~~~~~

* Pyramid expose() can decorate a generator function too


1.9.3 (2013-08-04)
~~~~~~~~~~~~~~~~~~

* Use setuptools instead of distribute


1.9.2 (2013-06-09)
~~~~~~~~~~~~~~~~~~

* New replaceable ``extract_parameters(request)`` static method on
  Pyramid's `expose` decorator

* **Backward incompatible change**: fix handling of bindparams in
  ProxiedQuery, which shall be passed as a dictionary with the
  `params` keyword instead as of individual keywords

* Fix handling of SQLAlchemy custom types


1.9.1 (2013-04-17)
~~~~~~~~~~~~~~~~~~

* Fix and test handling of ORM queries

* Fix Pyramid exposure of ORM queries


1.9 (2013-04-08)
~~~~~~~~~~~~~~~~

* Minor adjustments for SQLAchemy 0.8

* Compatibility tweaks for Python 2.7 and Python 3.3

* Improved test coverage


1.8.7 (2013-03-18)
~~~~~~~~~~~~~~~~~~

* For backward compatibility check for “filters” too

* Ignore the filter condition if the comparison value is missing


1.8.6 (2013-03-08)
~~~~~~~~~~~~~~~~~~

* Use the ExtJS default name, “filter”, not the plural form, “filters”
  for the filter parameter


1.8.5 (2013-02-28)
~~~~~~~~~~~~~~~~~~

* Factor out the extraction of filtering conditions, so it can be used
  by other packages


1.8.4 (2013-01-28)
~~~~~~~~~~~~~~~~~~

* Field metadata information can be a callable returning the actual
  dictionary


1.8.3 (2013-01-26)
~~~~~~~~~~~~~~~~~~

* **Backward incompatible change**: pass the request also the the
  ``save_changes`` function, it may need it to determine if the user
  is allowed to make the changes


1.8.2 (2013-01-21)
~~~~~~~~~~~~~~~~~~

* More generic way of specifying an handler for non-GET request
  methods


1.8.1 (2013-01-09)
~~~~~~~~~~~~~~~~~~

* **Backward incompatible change**: pass the request to the adaptor
  function, it may need it to do its job


1.8 (2012-12-19)
~~~~~~~~~~~~~~~~

* SQLAlchemy 0.8 compatibility


1.7.12 (2012-11-17)
~~~~~~~~~~~~~~~~~~~

* Properly recognize TIME type


1.7.11 (2012-10-22)
~~~~~~~~~~~~~~~~~~~

* Fix exception


1.7.10 (2012-10-22)
~~~~~~~~~~~~~~~~~~~

* Small code tweaks


1.7.9 (2012-10-20)
~~~~~~~~~~~~~~~~~~

* Attempt to extract the primary key fields of a ProxiedQuery


1.7.8 (2012-10-19)
~~~~~~~~~~~~~~~~~~

* More versatile way of injecting the SA session maker


1.7.7 (2012-09-26)
~~~~~~~~~~~~~~~~~~

* Multicolumns sort


1.7.6 (2012-09-25)
~~~~~~~~~~~~~~~~~~

* Better error reporting


1.7.5 (2012-09-21)
~~~~~~~~~~~~~~~~~~

* Rework how filters are passed

* Emit more compact JSON


1.7.4 (2012-09-14)
~~~~~~~~~~~~~~~~~~

* Tweak the Pyramid ``expose`` to work on selectables


1.7.3 (2012-09-12)
~~~~~~~~~~~~~~~~~~

* New ``expose`` decorator for Pyramid


1.7.2 (2012-08-18)
~~~~~~~~~~~~~~~~~~

* Ability to skip a field, setting its metadata info to ``False``

* Extract the primary key fields of a ProxiedEntity


1.7.1 (2012-08-13)
~~~~~~~~~~~~~~~~~~

* Pyramid glue


1.7 (2012-08-08)
~~~~~~~~~~~~~~~~

* Drop cjson support
