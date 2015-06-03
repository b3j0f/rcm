Reflective component model library for python.

.. image:: https://pypip.in/license/b3j0f.rcm/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.rcm/
   :alt: License

.. image:: https://pypip.in/status/b3j0f.rcm/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.rcm/
   :alt: Development Status

.. image:: https://pypip.in/version/b3j0f.rcm/badge.svg?text=version
   :target: https://pypi.python.org/pypi/b3j0f.rcm/
   :alt: Latest release

.. image:: https://pypip.in/py_versions/b3j0f.rcm/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.rcm/
   :alt: Supported Python versions

.. image:: https://pypip.in/implementation/b3j0f.rcm/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.rcm/
   :alt: Supported Python implementations

.. image:: https://pypip.in/format/b3j0f.rcm/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.rcm/
   :alt: Download format

.. image:: https://travis-ci.org/b3j0f/rcm.svg?branch=master
   :target: https://travis-ci.org/b3j0f/rcm
   :alt: Build status

.. image:: https://coveralls.io/repos/b3j0f/rcm/badge.png
   :target: https://coveralls.io/r/b3j0f/rcm
   :alt: Code test coverage

.. image:: https://pypip.in/download/b3j0f.rcm/badge.svg?period=month
   :target: https://pypi.python.org/pypi/b3j0f.rcm/
   :alt: Downloads

Links
-----

- `Homepage`_
- `PyPI`_
- `Documentation`_

Installation
------------

pip install b3j0f.rcm

Features
--------

A reflective component model eases the separation of concerns in any development project at run/compile-time in adding leazy coupling between objects and in separating business and non-functional code, whatever used languages and technologies.

In this implementation, python is used such as a pivotal language between programming languages and technologies.

This library is mainly inspirated from the projects `Fractal`_ and `FraSCAti`_ in adding more possibilities in usage with management of multiple cardinality in most layers and more lazy coupling without more complexity.

Therefore, reflective components provide:

- a business part which is a set of sub-components or Python code.
- a membrane which contains all non-functional components.
- binding specialization which distinguish what and how the business is provided/consumed.
- sharing of components allowing one component to be sub-component of several components like itself.
- a model where everything is a component (factories, bindings, membrane, etc.) in order to use the same logic everywhere in the component level, whatever functional or non-functional requirements.

A good way to play with rcm is to use a bootstrap component such as the entry point of component running.

A bootstrap component contains a component loader which manages component instantiation from code or configuration files.
All loaded components are included in the bootstrap components and becomes one of its children component.

A component inherits from a dictionary in order to access to component ports through __delitem__, __setitem__ and __getitem__ methods, and is hashable.

Here is a description of provided packages:

* b3j0f.rcm.core: default package which contains the definition of a Component.
* b3j0f.rcm.io: Input/Output Component management.
* b3j0f.rcm.nf: non-functional properties of components.
* b3j0f.rcm.factory: component factory definition.
* b3j0f.rcm.conf: component configuration.

Examples
--------

State of the art
----------------

Perspectives
------------

- Cython implementation.

Donation
--------

.. image:: https://cdn.rawgit.com/gratipay/gratipay-badge/2.3.0/dist/gratipay.png
   :target: https://gratipay.com/b3j0f/
   :alt: I'm grateful for gifts, but don't have a specific funding goal.

.. _Homepage: https://github.com/b3j0f/rcm
.. _Documentation: http://pythonhosted.org/b3j0f.rcm
.. _PyPI: https://pypi.python.org/pypi/b3j0f.rcm/
.. _Fractal: http://fractal.ow2.org/
.. _FraSCAti: http://wiki.ow2.org/frascati/Wiki.jsp?page=FraSCAti
