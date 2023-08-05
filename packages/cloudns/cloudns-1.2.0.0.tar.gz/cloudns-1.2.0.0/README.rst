YY cloudns API python client
============================

A python client for the YY cloudns API. A command line program is also
included.

Installation
------------

To install cloudns, simply:

.. code-block:: bash

   $ pip install cloudns


Quick Start
-----------

This client supports all functions defined in the API. To use those functions,
first create a User object, then call methods on it.

.. code-block:: pycon

   >>> import cloudns
   >>> u = cloudns.User('dw_foo', '8AFBE6DEA02407989AF4DD4C97BB6E25')
   >>> u.get_all_zones()
   ...
   >>> u.get_all_records('yyclouds.com')
   ...

Since most api function requires a zone to work on, you can create a zone from
a User and call methods on zone. Zone contains the most frequently used
functions from the API.

.. code-block:: pycon

   >>> z = u.zone('yyclouds.com')
   >>> z.create_record('test-foo', '8.8.8.8', 'tel')
   >>> z.get_records_by_name('test-foo')
   ...
   >>> z.delete_records_by_name('test-foo')
   ...

This client does very strict error checking. Everything from HTTP error to bad
response from cloudns server will raise an exception. All exceptions raised by
cloudns will be a subclass of CloudnsError.

.. code-block:: pycon

   >>> r = z.create_record('test-foo', '8.8.8.8', 'uni'); z.delete_record_by_id(r.rid)
   ... # Will raise exception. Pending record can not be deleted.


CLI usage
---------

This client includes a CLI script named cloudns. You can use it as a
interactive shell or as a command line program. This CLI script is available
in v1.1.1.0+.

Example usage:

As a normal command line program:

.. code-block:: bash

   cloudns --passport mypsp --token mytoken --zone myzone.com create abc 10.0.0.1 tel
   cloudns --passport mypsp --token mytoken --zone myzone.com create abc 10.0.0.1 uni
   cloudns --passport mypsp --token mytoken --zone myzone.com search abc
   cloudns --passport mypsp --token mytoken --zone myzone.com delete abc

As an interactive shell:

.. code-block:: bash

   $ cloudns --passport mypsp --token mytoken --zone myzone.com
   This is Cloudns REPL, an interactive shell for using cloudns.
   Type help or ? for usage

   cloudns> create abc 10.0.0.1 tel

   cloudns> create abc 10.0.0.1 uni

   cloudns> search abc
   2 record(s).
   abc.myzone.com	300	A	10.0.0.1	tel	ACTIVE
   abc.myzone.com	300	A	10.0.0.1	uni	ACTIVE

   cloudns> delete abc

   cloudns> search abc
   No record found.

   cloudns> exit
   $

For more information, see
https://cloudns.readthedocs.org/en/latest/cloudns_cli.html

Documentation
-------------

Cloudns API documentation is available at
http://www.nsbeta.info/doc/YY-DNS-API.pdf

Cloudns python client and cloudns CLI documentation is available at
https://cloudns.readthedocs.org/


ChangeLog
---------

* v1.2.0.0 2013-11-27

  - use upstream 1.2 api, this client is backward compatible with v1.1.1.3.
    It just use the new api.
  - minor, some spelling fixes

* v1.1.1.3 2013-11-08

  - add CLI program named cloudns
  - add test using tox

* v1.1.0.2 2013-08-31

  - package tested on python 2.6/2.7/3.3
  - bugfix: fix an import error on python 3.3

* v1.1.0.1 2013-08-13

  - initial release
