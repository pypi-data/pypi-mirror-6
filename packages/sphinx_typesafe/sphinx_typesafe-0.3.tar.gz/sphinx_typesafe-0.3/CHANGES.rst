CHANGES
=======

0.3 (13-feb-2014)
-----------------

* Several bugfixes and enhancements

    * better resolution of type names

    * fix support for methods

    * fix documentation

    * test suite now has 60 test cases

    * support for types.NoneType

    * more restrictive matching of documenation against parameters

    * support for ignoring type checking: types.NotImplementeType

    * exposing function ``get_class_type``


0.2 (03-dec-2013)
-----------------

* Full code rewiew and rewrite by Richard Gomes <rgomes.info@gmail.com>

    * @typesafe is now a class

    * Code reorganization and some optimization

    * Preparing code for porting to Python3

* New features

    * Added verification of return type of decorated functions

* Bugfixes

    * Type resolver now finds types involving multiple nested modules

    * Type resolver assumes module '__builtin__' for simple names, such as 'bool'

* Renamed to *sphinx_typesafe*

* Documentation rewriten in reStructuredText

* Added *docs* directory required by readthedocs.org

* First version deployed onto PyPI


0.1
---

Original version of IcanHasTypeCheck (ICHTC) by Klaas <khz@tzi.org>
