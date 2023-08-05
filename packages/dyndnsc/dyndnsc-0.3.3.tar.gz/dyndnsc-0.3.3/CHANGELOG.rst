Release history
===============

0.3.3 (02.12.2013)
++++++++++++++++++
- added: experimental support for http://freedns.afraid.org
- added: detecting ipv6 addresses using 'webcheck6' or 'webcheck46'
- fixed: long outstanding state bugs in detector base class
- improved: input validation in Iface detection
- improved: support pytest conventions

0.3.2 (16.11.2013)
++++++++++++++++++
- added: command line option --debug to explicitly increase loglevel 
- fixed potential race issues in detector base class
- fixed: several typos, test structure, naming conventions, default loglevel
- changed: dynamic importing of detector code

0.3.1 (November 2013)
+++++++++++++++++++++
- added: support for https://nsupdate.info
- fixed: automatic installation of 'requests' with setuptools dependencies
- added: more URL sources for 'webcheck' IP detection
- improved: switched optparse to argparse for future-proofing
- fixed: logging initialization warnings
- improved: ship tests with source tarball
- improved: use reStructuredText rather than markdown

0.3  (October 2013)
+++++++++++++++++++
- moved project to https://github.com/infothrill/python-dyndnsc
- added continuous integration tests using http://travis-ci.org
- added unittests
- dyndnsc is now a package rather than a single file module
- added more generic observer/subject pattern that can be used for
  desktop notifications
- removed growl notification
- switched all http related code to the "requests" library
- tentatively added http://www.noip.com
- removed dyndns.majimoto.net
- dropped support for python <= 2.5 and added support for python 3.2+

0.2.1 (February 2013)
+++++++++++++++++++++
- moved code to git
- minimal PEP8 changes and code restructuring
- provide a makefile to get dependencies using buildout

0.2.0 (February 2010)
+++++++++++++++++++++
- updated IANA reserved IP address space
- Added new IP Detector: running an external command
- Minimal syntax changes based on the 2to3 tool, but remaining compatible 
  with python 2.x

0.1.2 (July 2009)
+++++++++++++++++
- Added a couple of documentation files to the source distribution

0.1.1 (September 2008)
++++++++++++++++++++++
- Focus: initial public release