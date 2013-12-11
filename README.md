PyRCM
=====

Python Reflective Component Model

PyRCM provides a reflective component architecture and runtime in order to add reflective properties to business classes or functions.

The project contains those items:
- doc: directory which contains all documentation related to this library.
- src: directory which contains all library sources.
- examples: directory which contains examples of library usages.
- LICENSE: license contract.
- README.md: this readme.

Library description:

Everything starts with a bootstrap components which is the entry point of component running.

A bootstrap component contains a component loader which manages component instantiation from code or configuration files.
All loaded components are included in the bootstrap components and becomes one of its children component.

A component inherits from a dictionary in order to access to component interfaces through __delitem__, __setitem__ and __getitem__ methods.

By default, the loaded component provides business methods coming from the embedded implementation.

Here is a description of packages:

* pyrcm: default package, contains modules core and packages binding, controller, decorator, factory and parser.

* pyrcm.core: contains definition of Component (base class for every object in this library), Interface, Binding and get_config() and get_bootstrap_component() method which allows to get the bootstrap component and starts to load components.

* pyrcm.binding: contains binding types such as python (default), REST, etc.

* pyrcm.decorator: contains all decorators useful to complete component configuration.

* pyrcm.factory: contains all types of component factories.

* pyrcm.parser: contains components with component configuration rules (files of kind sca, json, xml, etc.).
