Cloudant-Python
===============

|Build Status| |Coverage Status| |PyPi version| |PyPi downloads|

An effortless Cloudant / CouchDB interface for Python.

Install
-------

::

    pip install cloudant

Usage
-----

Cloudant-Python is a wrapper around Python
`Requests <http://www.python-requests.org/en/latest/>`__ for interacting
with CouchDB or Cloudant instances. Check it out:

.. code:: python

    import cloudant

    # connect to your account
    # in this case, https://garbados.cloudant.com
    USERNAME = 'garbados'
    account = cloudant.Account(USERNAME)

    # login, so we can make changes
    login = account.login(USERNAME, PASSWORD)
    assert login.status_code == 200

    # create a database object
    db = account.database('test')

    # now, create the database on the server
    response = db.put()
    print response.json()
    # {'ok': True}

HTTP requests return
`Response <http://www.python-requests.org/en/latest/api/#requests.Response>`__
objects, right from
`Requests <http://www.python-requests.org/en/latest/>`__.

Cloudant-Python can also make asynchronous requests by passing
``async=True`` to an object's constructor, like so:

.. code:: python

    import cloudant

    # connect to your account
    # in this case, https://garbados.cloudant.com
    USERNAME = 'garbados'
    account = cloudant.Account(USERNAME, async=True)

    # login, so we can make changes
    future = account.login(USERNAME, PASSWORD)
    # block until we get the response body
    login = future.result()
    assert login.status_code == 200

Asynchronous HTTP requests return
`Future <http://docs.python.org/dev/library/concurrent.futures.html#future-objects>`__
objects, which will await the return of the HTTP response. Call
``result()`` to get the
`Response <http://www.python-requests.org/en/latest/api/#requests.Response>`__
object.

See the `API
reference <http://cloudant-labs.github.io/cloudant-python/#api>`__ for
all the details you could ever want.

Philosophy
----------

Cloudant-Python is minimal, performant, and effortless. Check it out:

Pythonisms
~~~~~~~~~~

Cloudant and CouchDB expose REST APIs that map easily into native Python
objects. As much as possible, Cloudant-Python uses native Python objects
as shortcuts to the raw API, so that such convenience never obscures
what's going on underneath. For example:

.. code:: python

    import cloudant

    account = cloudant.Account('garbados')
    db = account.database('test')
    same_db = account['test']
    assert db.uri == same_db.uri
    # True

Cloudant-Python expose raw interactions -- HTTP requests, etc. --
through special methods, so we provide syntactical sugar without
obscuring the underlying API. Built-ins, such as ``__getitem__``, act as
Pythonic shortcuts to those methods. For example:

.. code:: python

    import cloudant

    account = cloudant.Account('garbados')

    db_name = 'test'
    db = account.database(db_name)
    doc = db.document('test_doc')

    # create the document
    resp = doc.put(params={
      '_id': 'hello_world',
      'herp': 'derp'
      })

    # delete the document
    rev = resp.json()['_rev']
    doc.delete(rev).raise_for_status()

    # but this also creates a document
    db['hello_world'] = {'herp': 'derp'}

    # and this deletes the database
    del account[db_name]

Iterate over Indexes
~~~~~~~~~~~~~~~~~~~~

Indexes, such as `views <https://cloudant.com/for-developers/views/>`__
and Cloudant's `search
indexes <https://cloudant.com/for-developers/search/>`__, act as
iterators. Check it out:

.. code:: python

    import cloudant

    account = cloudant.Account('garbados')
    db = account.database('test')
    view = db.all_docs() # returns all docs in the database
    for doc in db:
      # iterates over every doc in the database
      pass
    for doc in view:
      # and so does this!
      pass
    for doc in view.iter(descending=True):
      # use `iter` to pass options to a view and then iterate over them
      pass

`Behind the
scenes <https://github.com/cloudant-labs/cloudant-python/blob/master/cloudant/index.py#L23-L33>`__,
Cloudant-Python yields documents only as you consume them, so you only
load into memory the documents you're using.

Special Endpoints
~~~~~~~~~~~~~~~~~

If CouchDB has a special endpoint for something, it's in Cloudant-Python
as a special method, so any special circumstances are taken care of
automagically. As a rule, any endpoint like ``_METHOD`` is in
Cloudant-Python as ``Object.METHOD``. For example:

-  ``https://garbados.cloudant.com/_all_dbs`` ->
   ``Account('garbados').all_dbs``
-  ``http://localhost:5984/DB/_all_docs`` ->
   ``Account().database(DB).all_docs()``
-  ``http://localhost:5984/DB/_design/DOC/_view/INDEX`` ->
   ``Account().database(DB).design(DOC).view(INDEX)``

Asynchronous
~~~~~~~~~~~~

If you instantiate an object with the ``async=True`` option, its HTTP
request methods (such as ``get`` and ``post``) will return
`Future <http://docs.python.org/dev/library/concurrent.futures.html#future-objects>`__
objects, which represent an eventual response. This allows your code to
keep executing while the request is off doing its business in
cyberspace. To get the
`Response <http://www.python-requests.org/en/latest/api/#requests.Response>`__
object (waiting until it arrives if necessary) use the ``result``
method, like so:

.. code:: python

    import cloudant

    account = cloudant.Account(async=True)
    db = account['test']
    future = db.put()
    response = future.result()
    print db.get().result().json()
    # {'db_name': 'test', ...}

As a result, any methods which must make an HTTP request return a
`Future <http://docs.python.org/dev/library/concurrent.futures.html#future-objects>`__
object.

Option Inheritance
~~~~~~~~~~~~~~~~~~

If you use one object to create another, the child will inherit the
parents' settings. So, you can create a ``Database`` object explicitly,
or use ``Account.database`` to inherit cookies and other settings from
the ``Account`` object. For example:

.. code:: python

    import cloudant

    account = cloudant.Account('garbados')
    db = account.database('test')
    doc = db.document('test_doc')

    url = 'https://garbados.cloudant.com'
    path = '/test/test_doc'
    otherdoc = cloudant.Document(url + path)

    assert doc.uri == otherdoc.uri
    # True

Testing
-------

To run Cloudant-Python's tests, just do:

::

    python setup.py test

Documentation
-------------

The API reference is automatically generated from the docstrings of each
class and its methods. To install Cloudant-Python with the necessary
extensions to build the docs, do this:

::

    pip install -e cloudant[docs]

Then, in Cloudant-Python's root directory, do this:

::

    python docs

Note: docstrings are in
`Markdown <http://daringfireball.net/projects/markdown/>`__.

License
-------

`MIT <http://opensource.org/licenses/MIT>`__, yo.

.. |Build Status| image:: https://travis-ci.org/cloudant-labs/cloudant-python.png
   :target: https://travis-ci.org/cloudant-labs/cloudant-python
.. |Coverage Status| image:: https://coveralls.io/repos/cloudant-labs/cloudant-python/badge.png
   :target: https://coveralls.io/r/cloudant-labs/cloudant-python
.. |PyPi version| image:: https://pypip.in/v/cloudant/badge.png
   :target: https://crate.io/packages/cloudant/
.. |PyPi downloads| image:: https://pypip.in/d/cloudant/badge.png
   :target: https://crate.io/packages/cloudant/
