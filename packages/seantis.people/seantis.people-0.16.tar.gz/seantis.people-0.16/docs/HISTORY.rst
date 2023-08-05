
Changelog
---------

0.16 (2013-12-31)
~~~~~~~~~~~~~~~~~

- Fixes a number of issues with zodb membership source.
  [href]

- Adds the ability to define custom membership functions on the detail view.
  [href]

- Adds the ability to define custom compound columns in other packages.
  [href]

- Adds missing profile dependencies for membership type.
  [href]

- Hides start/end on memberships, until it is properly implemented.
  [href]


0.15
~~~~

- Adds very basic json export people list.
  [href]

0.14
~~~~

- Adds the ability to import images through urls.
  [href]

- Organizations defined through memberships are now clickable in the list
  view. This is the default in the standard type.
  [href]

- Adds a standard profile which is more or less compatible with 
  egov.contactdirectory. Fixes #6.
  [href]

- Rename responsive-table to responsive to be compatible with latest
  plonetheme.onegov release.
  [href]

- Adds custom event to signal changes in memberships.
  [href]

- Updates German translation.
  [href]

0.13
~~~~

- Adds the ability to install and upgrade profiles with custom people types.
  This can be done using the new seantis people controlpanel.
  [href]

- Removes import action from PHZ type.
  [href]

- Renames PHZ to PH Zug.
  [href]

- Ensures that imported strings are stripped of their whitespace in front and
  at the end.
  [href]

- Redirect to person list after succesful import.
  [href]

- Fixes required fields error not showing up on import.
  [href]

0.12
~~~~

- PHZ portrait should be optional.
  [href]

0.11
~~~~

- Supports new responsive-table helper in plonetheme.onegov.
  [href]

- Hides first-/lastname on PHZ detail view.
  [href]

- Adds link to a detailed portrait of the employee for the PHZ.
  [href]

0.10
~~~~

- Changes German translation of "Organisation Unit 2" for PHZ.
  [href]

0.9
~~~

- Adds membership rendering to detail view.
  [href]

0.8
~~~

- Adds collective.cover support as an extra
  [href]

- Memberships can now be defined dynamically through the MembershipSource 
  adapter.
  [href]

0.7
~~~

- Hide label of images in the detail view.
  [href]

- Adds rendering support for these field types: Text, RichText, Lists.
  [href]

- Adds custom type for Pädagogische Hochschule Zug.
  [href]

- Adds ability to filter attributes returning lists in the table.
  [href]

- Adds ability to use custom titles on columns.
  [href]

0.6
~~~

- Adds detail view with configurable positioning through schema attributes.
  [href]

- Fixes not showing the selected filter after a refresh.
  [href]

0.5
~~~

- Supports supermodel security permissions in the people's list (giving the
  ability to hide certain fields in the table depending on the user).
  [href]

- Fixes filter.js being unable to filter for empty values.
  [href]

0.4
~~~

- Ensures that the title is updated when the object is modified.
  [href]

- The first letters are now taken from the sorted title.
  [href]

- The title attributes order is now independent of the field order.
  [href]

- Fixes a number of unicode issues.
  [href]

0.3
~~~

(skipped by accident)

0.2
~~~

- People are now sorted by unicode collation.
  [href]

- The people can be filtered by the first litter of the title.
  [href]

0.1
~~~

- Initial release.
  [href]
