Seantis People
==============

A list of people, optionally organized by organisations and positions.

Municiaplities for which we contribute to `OneGov`_ often require a public list
of contacts. For the customers and us this package needs to scratch the
following itches:

- The directory must not force a set of fields on the user. Each customer
  should have the option to create its own set of fields. At the same time
  there should be at least one reasonable standard.

- Some fields should only be visible with certain permissions. Think mobile
  phone number.

- Elected officials are part of many comitees and councils. It must be easy
  to define the timespans during which any person was part of such an
  organization. It must also always be clear what the role of the person was.

Design
------

This is how we plan to scratch the aforementioned itches:

- We give the user the possiblity to define a list of people. Each list
  consists of a number of dexterity objects with IPerson behavior. Within
  one list only one dexterity type is allowed.

- Through the schema of the dexterity type we define the fields, their
  required read and write permissions, the fields shown in the list, the order
  of those fields, the fields available for filtering in the list, and the 
  fields shown in the detail view.

- These dexterity types may be installed by any package or they may be included
  in seantis.people, available through separate profiles. (It's technically
  even possible to create them through the web, but we don't recommend this
  approach for various reasons.)

- We devine an organzation-behavior which any folderish dexterity type may 
  adapt. Types with that behavior may then have people added to them with
  entry, exit and role information.

- We display the memberships of each person using the entry, exit and role
  information. We identity the organization solely by url and title. This will
  give users the ability to have some plone page act as an organization, which
  frees os from having to reinvent the wheel there.

Status
------

The people types and list are pretty much ready for a first release. We are
currently working on the organisation part of the module.

Known Issues
------------

After a reindex, the people's list no longer shows the organization memberships.
This is documented with a workaround in the following issue:

https://github.com/seantis/seantis.people/issues/10

Alternatives
------------

Close to our requirements (but no cigar):
https://github.com/collective/collective.contact.core

Requirements
------------

-  Python 2.7
-  Plone 4.3+
-  Linux / Posix ( Windows may or may not work )

Build Status
------------

.. image:: https://travis-ci.org/seantis/seantis.people.png   
  :target: https://travis-ci.org/seantis/seantis.people
  :alt: Build Status

Coverage
--------

.. image:: https://coveralls.io/repos/seantis/seantis.people/badge.png?branch=master
  :target: https://coveralls.io/r/seantis/seantis.people?branch=master
  :alt: Project Coverage

Latests PyPI Release
--------------------
.. image:: https://pypip.in/v/seantis.people/badge.png
  :target: https://crate.io/packages/seantis.people
  :alt: Latest PyPI Release

License
-------
seantis.people is released under GPL v2


.. -> external links

.. _OneGov: http://onegov.ch/