.. Voyeur documentation master file, created by
   sphinx-quickstart on Mon Feb 24 13:55:51 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Voyeur
======

.. image:: https://api.travis-ci.org/gilles/voyeur.png?branch=master
        :target: https://api.travis-ci.org/gilles/voyeur


Voyeur is an simple library to serialize an object into another object.

The goal is to create a representation that is easily `json.dumps()` friendly.

I've made it while working with datastore such as Riak, MongoDB or CouchBase where the response is a dict and
I wanted to transform it into another dict for API output.

Quickstart
----------

It's as easy as this:

.. code-block:: python

    from voyeur import view

    definition = {
        'id': int
    }

    data = {
        'id': '1'
    }

    result = view(data, definition)
    assert result = {'id' : 1}

The definition is a dictionary with key/callable pairs. Voyeur will use the key to get the value from the data then apply the callable.

Using objects
-------------

That works too:

.. code-block:: python

    from voyeur import view

    definition = {
        'id': int
        'prop': int
    }

    class Data(object):
        id = 1

        @property
        def prop(self):
            return "12"

    result = view(Data(), definition)
    assert result = {'id' : 1, 'prop' : 12}


Using runtime parameters
------------------------

A callable can take any kwargs and use them

.. code-block:: python

    from voyeur import view

    def mycallable(value, test=None):
        return "foo:%s:%s" % (value, test)

    definition = {
        'id': int
        'prop': mycallable
    }

    class Data(object):
        id = 1

        @property
        def prop(self):
            return "12"

    result = view(Data(), definition, test='bar')
    assert result = {'id' : 1, 'prop' : 'foo:12:bar'}

More complex types
------------------

Voyeur can take a class as a callable if it inherits from :py:class:`voyeur.types.Type`. This allows building more complex serializer.

A good example is the :py:class:`voyeur.types.Type` that reads the value from a different field.

.. code-block:: python

    from voyeur import view
    definition = {
        'field': DeferredType('anotherfield', int),
    }

    data = {'anotherfield': '2'}
    result = view(data, definition)
    assert result == {'field':2}


Indices and tables
==================

.. toctree::
   :maxdepth: 2

   api

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
