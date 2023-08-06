Sous-chef
=========

.. image:: https://pypip.in/v/sous-chef/badge.png
    :target: https://pypi.python.org/pypi/sous-chef
    :alt: Latest PyPI version

A small webapp for viewing and searching Chef nodes.

Usage
-----

::

	gunicorn 'sous_chef:create_app()'

The optional environment variable ``SOUS_CHEF_SETTINGS`` can be pointed at a
Flask configuration file (`docs`_).

The app can be run in debug mode by using the `create_debug_app` function:

::

	gunicorn 'sous_chef:create_debug_app()'

The ``flask-debugtoolbar`` package is availible, the DebugToolbar extension will
be used.

.. _docs: http://flask.pocoo.org/docs/config/#configuring-from-files

Installation
------------

::

	pip install sous-chef gunicorn

Requirements
^^^^^^^^^^^^

Requires `Flask`_ and `PyChef`_. `Gunicorn`_ is the simplest method of
deployment, but is not a requirement (allowing alternate WSGI servers to be
used). Optionally uses `Flask Debug Toolbar`_ using the debug application.

.. _Flask: http://flask.pocoo.org/
.. _PyChef: https://github.com/coderanger/pychef
.. _Gunicorn: http://gunicorn.org/
.. _Flask Debug Toolbar: https://pypi.python.org/pypi/Flask-DebugToolbar
