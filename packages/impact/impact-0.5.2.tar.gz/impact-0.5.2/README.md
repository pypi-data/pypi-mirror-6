Impact
------

*Impact* is a Modelica package manager.

![ImpactLogo](https://rawgithub.com/xogeny/impact/master/images/logo_glossy.svg)

Conventions
-----------

*Impact* follows a "convention over configuration" philosophy.  That
means that if you follow some reasonable conventions (that generally
reflect best practices), the system should work without the need for
any manual configuration.  Here are the conventions that *Impact* expects:

* The name of the repository should match (case included) the name
  of your library.

* Semantic Versioning - To identify a library release, simply
  attach a tag to the release that is a [semantic
  version](http://semver.org) (an optional "v" at the start of the
  tag name is allowed).

* Place the `package.mo` file for your library in one of the
  following locations within the repository:

  * `./package.mo` (i.e., at the root of the repository)

  * `./<LibraryName>/package.mo` (i.e., within a directory sharing
    the name of the library)

  * `./<LibraryName> <Version>/package.mo` (i.e., within a directory sharing
    the name of the library followed by a space followed by the tag name,
    without any leading `v` present)

Development
-----------

The development takes place on https://github.com/xogeny/impact
