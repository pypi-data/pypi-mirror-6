Changelog
---------

0.6.2 (2014-03-09)
++++++++++++++++++

- Fixed: Project resource ``status`` attribute was converted to IssueStatus resource by mistake

0.6.1 (2014-02-27)
++++++++++++++++++

- Fixed: `Issue #10 <https://github.com/maxtepkeev/python-redmine/issues/10>`__ (Python
  Redmine was incorrectly raising ``ResourceAttrError`` while creating some resources via
  ``new()`` method)

0.6.0 (2014-02-19)
++++++++++++++++++

- Added: ``Redmine.auth()`` shortcut for the case if we just want to check if user provided
  valid auth credentials, can be used for user authentication on external resource based on
  Redmine user database (see `docs <http://python-redmine.readthedocs.org/advanced/
  external_auth.html>`__ for details)
- Fixed: ``JSONDecodeError`` was raised in some Redmine versions during some create/update
  operations (thanks to `0x55aa <https://github.com/0x55aa>`__)
- Fixed: User resource ``status`` attribute was converted to IssueStatus resource by mistake

0.5.0 (2014-02-09)
++++++++++++++++++

- Added: An ability to create custom resources which allow to easily redefine the behaviour
  of existing resources (see `docs <http://python-redmine.readthedocs.org/advanced/
  custom_resources.html>`__ for details)
- Added: An ability to add/remove watcher to/from issue (see `docs
  <http://python-redmine.readthedocs.org/resources/issue.html#watchers>`__ for details)
- Added: An ability to add/remove users to/from group (see `docs
  <http://python-redmine.readthedocs.org/resources/group.html#users>`__ for details)

0.4.0 (2014-02-08)
++++++++++++++++++

- Added: New exceptions:

  * ConflictError
  * ReadonlyAttrError
  * ResultSetTotalCountError
  * CustomFieldValueError

- Added: Update functionality via ``update()`` and ``save()`` methods for resources (see
  `docs <http://python-redmine.readthedocs.org/operations.html#update>`__ for details):

  * User
  * Group
  * IssueCategory
  * Version
  * TimeEntry
  * ProjectMembership
  * WikiPage
  * Project
  * Issue

- Added: Limit/offset support via ``all()`` and ``filter()`` methods for resources that
  doesn't support that feature via Redmine:

  * IssueRelation
  * Version
  * WikiPage
  * IssueStatus
  * Tracker
  * Enumeration
  * IssueCategory
  * Role
  * Group
  * CustomField

- Added: On demand includes, e.g. in addition to ``redmine.group.get(1, include='users')``
  users for a group can also be retrieved on demand via ``group.users`` if include wasn't set
  (see `docs <http://python-redmine.readthedocs.org/resources/index.html>`__ for details)
- Added: ``total_count`` attribute to ResourceSet object which holds the total number
  of resources for the current resource type available in Redmine (thanks to
  `Andrei Avram <https://github.com/andreiavram>`__)
- Added: An ability to return ``None`` instead of raising a ``ResourceAttrError`` for all
  or selected resource objects via ``raise_attr_exception`` kwarg on Redmine object (see
  `docs <http://python-redmine.readthedocs.org/configuration.html#exception-control>`__ for
  details or `Issue #6 <https://github.com/maxtepkeev/python-redmine/issues/6>`__)
- Added: ``pre_create()``, ``post_create()``, ``pre_update()``, ``post_update()`` resource
  object methods which can be used to execute tasks that should be done before/after
  creating/updating the resource through ``save()`` method
- Added: Allow to create resources in alternative way via ``new()`` method (see `docs
  <http://python-redmine.readthedocs.org/operations.html#new>`__ for details)
- Added: Allow daterange TimeEntry resource filtering via ``from_date`` and ``to_date``
  keyword arguments (thanks to `Antoni Aloy <https://github.com/aaloy>`__)
- Added: An ability to retrieve Issue version via ``version`` attribute in addition to
  ``fixed_version`` to be more obvious
- Changed: Documentation for resources rewritten from scratch to be more understandable
- Fixed: Saving custom fields to Redmine didn't work in some situations
- Fixed: Issue's ``fixed_version`` attribute was retrieved as dict instead of Version resource
  object
- Fixed: Resource relations were requested from Redmine every time instead of caching the
  result after first request
- Fixed: `Issue #2 <https://github.com/maxtepkeev/python-redmine/issues/2>`__ (limit/offset
  as keyword arguments were broken)
- Fixed: `Issue #5 <https://github.com/maxtepkeev/python-redmine/issues/5>`__ (Version
  resource ``status`` attribute was converted to IssueStatus resource by mistake) (thanks
  to `Andrei Avram <https://github.com/andreiavram>`__)
- Fixed: A lot of small fixes, enhancements and refactoring here and there

0.3.1 (2014-01-23)
++++++++++++++++++

- Added: An ability to pass Requests parameters as a dictionary via ``requests`` keyword
  argument on Redmine initialization, i.e. Redmine('\http://redmine.url', requests={}).
- Fixed: `Issue #1 <https://github.com/maxtepkeev/python-redmine/issues/1>`__ (unable
  to connect to Redmine server with invalid ssl certificate).

0.3.0 (2014-01-18)
++++++++++++++++++

- Added: Delete functionality via ``delete()`` method for resources (see `docs
  <http://python-redmine.readthedocs.org/operations.html#delete>`__ for details):

  * User
  * Group
  * IssueCategory
  * Version
  * TimeEntry
  * IssueRelation
  * ProjectMembership
  * WikiPage
  * Project
  * Issue

- Changed: ResourceManager ``get()`` method now raises a ``ValidationError`` exception if
  required keyword arguments aren't passed

0.2.0 (2014-01-16)
++++++++++++++++++

- Added: New exceptions:

  * ServerError
  * NoFileError
  * ValidationError
  * VersionMismatchError
  * ResourceNoFieldsProvidedError
  * ResourceNotFoundError

- Added: Create functionality via ``create()`` method for resources (see `docs
  <http://python-redmine.readthedocs.org/operations.html#create>`__ for details):

  * User
  * Group
  * IssueCategory
  * Version
  * TimeEntry
  * IssueRelation
  * ProjectMembership
  * WikiPage
  * Project
  * Issue

- Added: File upload support, see ``upload()`` method in Redmine class
- Added: Integer representation to all resources, i.e. ``__int__()``
- Added: Informal string representation to all resources, i.e. ``__str__()``
- Changed: Renamed ``version`` attribute to ``redmine_version`` in all resources to avoid
  name intersections
- Changed: ResourceManager ``get()`` method now raises a ``ResourceNotFoundError`` exception
  if resource wasn't found instead of returning None in previous versions
- Changed: reimplemented fix for ``__repr__()`` from 0.1.1
- Fixed: Conversion of issue priorities to enumeration resource object didn't work

0.1.1 (2014-01-10)
++++++++++++++++++

- Added: Python 2.6 support
- Changed: WikiPage resource ``refresh()`` method now automatically determines it's project_id
- Fixed: Resource representation, i.e. ``__repr__()``, was broken in Python 2.7
- Fixed: ``dir()`` call on a resource object didn't work in Python 3.2

0.1.0 (2014-01-09)
++++++++++++++++++

- Initial release
