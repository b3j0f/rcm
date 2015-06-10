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

The Reflective Component Model, ``RCM``, makes easier the development of softwares in focusing in separation of concerns (SoC_) thanks to a lazy and dynamic coupling between business and non-functional code. This SoC provides several powerful paradigms such as Dependency Injection (DI_), Inversion of Control (IoC_), and so on... whatever used programming languages and technologies.

In this project, python is used such as a pivotal language between programming languages and technologies.

Therefore, RCM provides:

- a model where everything is a reflective component (component, controller, port, component factory, etc.) with the same reflective API.
- component (re-)configuration tools in order to ease distributed development, deployment and execution.
- binding specialization which distinguish what and how the business is provided/consumed.
- sharing of components allowing one component to be embedded by several components.

This model has a specific definition about component behavior. Components are a set of resources which contribute in its behavior. In such point of view, level of contribution is defined by the type of resources. By default, component resources might be seen suuch as embedded into the component. Once you accept this definition, you can use a port, which is a specific type of components which is bound to other ports in order improve a lazy coupling between components. Such ports are parts of the component non-functional properties, therefore, they are not impacted by component business state.

Here is a description of provided packages:

* b3j0f.rcm.core: default package which contains the definition of a Component.
* b3j0f.rcm.io: Input/Output Component management.
* b3j0f.rcm.nf: non-functional properties of components.
* b3j0f.rcm.conf: component configuration and factory definition.

It is possible to install any of previous package independently from others in using the command:

``pip install b3j0f.rcm-X``

where ``X`` is among {``core``; ``io``; ``nf``; ``conf``}

Examples
--------

State of the art
----------------

This library is mainly inspirated from the projects `Fractal`_ and `FraSCAti`_ in adding more possibilities in usage with management of multiple cardinality in most layers and more lazy coupling without more complexity.

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
.. _IoC: http://en.wikipedia.org/wiki/Inversion_of_control
.. _DI: http://en.wikipedia.org/wiki/Dependency_injection
.. _SoC: http://en.wikipedia.org/wiki/Separation_of_concerns
