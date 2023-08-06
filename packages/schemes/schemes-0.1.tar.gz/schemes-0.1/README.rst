=======
Schemes
=======


Schemes is a library for validating and deserializing input obtained via JSON,
XML, msgpack or other similar formats, and for preparing data for serialization
for output to the same formats and/or for persistence (typically, but not
exclusively, to a cache or a NoSQL data store).


Overview
--------

In order to use Schemes, you need at first to define one or more schemas::

    user_schema = Schema({'id': ReadOnly(Long()),
                          'username': String(min_length=3, max_length=16),
                          'fullname': Optional(String()),
                          'password': WriteOnly(String(min_length=8))})

You can then use the schema definition to create a document from input data::

    try:
        user = user_schema.create(
            {'username': u'tawmas', 'password': u'supersecret'})
    except ValidationError as error:
        print(error.reason)

All fields are implicitly treated as mandatory, unless marked with a modifier
such as ``Optional``, ``ReadOnly`` or ``Internal``. If one or more validation
errors occurr, Schemes will report all validation errors in a friendly
dictionary structure.

You can update an existing document from new input data::

    try:
        user = user_schema.patch(user, {'password': u'verysecure'})
    except ValidationError as error:
        print(error.reason)

``patch()`` accepts partial inputs, and it only overwrites the fields which are
actually present in the input data.

Finally, you can leverage the schema to prepare a document for output::

    representation = user_schema.emit(user)

This gives you a dictionary representation of your document suitable to be
serialized. Non-public fields are omitted, and some field types are converted
to a serialization friendly formats (for example, datetimes are emitted as RFC
3339 strings).


Early prerelease warning
------------------------

Schemes is at an early prerelease stage. As such, the public interface may well
change, and no documentation is available yet except for the Overview_ above.

Full documentation will be made available when the project reaches the beta
stage. In the meanwhile, you can have a look at the tests, especially the
integration tests in ``tests/integration``.

Initial development is on Python 2.7. The code is expected, and periodically
tested, to work on pypy, and it is expected to break on Python 3. Full support
for pypy and Python 3.3+ are planned for a later alpha stage.


Features and roadmap
--------------------

* Validation and conversion from a serialized format for document creation
  and update.

* Conversion to a serializable external representation.

* Conversion to a serializable internal representation (PLANNED).

* Coercion of raw data (e.g. from a database or a cache) without triggering
  full validation (PROVISIONAL IMPLEMENTATION).

* Easily extensible.

* Many field types supported out of the box:

  * booleans
  * integers
  * longs
  * floats
  * decimals (PLANNED)
  * unicode strings
  * encoded bytestrings (PLANNED)
  * datetimes
  * dates
  * lists
  * embedded schemas

* Many field modifiers supported out of the box: optional (with or without a
  default value), read-only (with optional automatic creation and update
  values), write-only, internal.

* Support custom rules on existing field types (PLANNED).

* Alternate declarative syntax (PLANNED).

* Versioned schemas with automatic upgrade and downgrade of documents (PLANNED).


Installing Schemes
------------------

You can install Schemes with pip::

    pip install schemes

If you want to hack on Schemes or run the test suite, you will also need to
install ``pytest``, and optionally the ``pytest-cov`` extension. You can
automatically install Schemes and its testing dependencies with pip::

    pip install schemes[testing]


License
-------

Schemes is an open source project by `Tommaso R. Donnarumma`_, distributed under
the MIT license. See the ``LICENSE`` file for details.

Schemes comes with an embedded copy of the `python-rfc3339`_ library by LShift
Ltd., which is also distributed under the MIT license.

.. _Tommaso R. Donnarumma: http://www.tawmas.net/
.. _python-rfc3339: https://github.com/tonyg/python-rfc3339
