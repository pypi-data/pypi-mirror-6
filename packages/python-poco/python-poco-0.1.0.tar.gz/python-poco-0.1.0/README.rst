===========
python-poco
===========

python-poco provides classes that can be used to integrate your software with
the South African postal code lookup service at http://poco.co.za.  Basic usage
is crazy simple::

    #!/usr/bin/env python

    from poco.poco import PocoSearcher

    results = PocoSearcher.results_as_dicts('Wingate Park')
    objects = PocoSearcher.results_as_objects('Wingate Park')

In the above example, 'results' is a list which contains dictionaries with the
following keys: ``id``, ``suburb``, ``area``, ``postal``, ``street``.
Similarly, 'objecst' is a list which contains objects of the ``PocoLocation``
class.  The ``PocoLocation`` class has the same keys mentioned above as class
attributes.  So basically, use ``results_as_dicts`` or ``results_as_objects``,
depending on what your application needs.

**One important caveat:**  The following rules apply:

* The search term cannot be empty.

* The search term must contain at least 3 characters.

An exception of type ``requests.exceptions.HTTPError`` will be raised if the above
requirements are not met.

For reference, the Poco API documentation is available at
http://poco.co.za/api/.
