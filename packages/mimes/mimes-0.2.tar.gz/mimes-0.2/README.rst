mimes
=====

.. image:: https://travis-ci.org/mbr/mimes.png?branch=master
   :target: https://travis-ci.org/mbr/mimes

An internet MIME-message is usually accompanied by a content-type string like
``text/plain`` or ``application/collection+json``. The mimes library allows
parsing these and can if types are subsets of another -- a parser that handles
``application/json``, for example, will be perfectly fine handing the
collection+json type with less semantics.

It also parses more complex strings including parameters (e.g.
``application/vnd.company.someapi; version=3``) and can construct these as
well.

See the `docs <http://pythonhosted.org/mimes>`_ for details.
