Changelog
=========

1.5.2 (2014-01-26)
------------------

- Another fix to include CHANGELOG.rst in the release.
  [zupo]


1.5.1 (2014-01-26)
------------------

- Include .rst files in release.
  [zupo]


1.5 (2014-01-26)
----------------

- Also set ``product_id`` on already existing members.
  [zupo]


1.4 (2013-10-07)
----------------

- @@validity view raises ConflictError on busy site, solved by
  committing transaction after every disabled user.
  [Matej Cotman]


1.3 (2013-01-08)
----------------

- Prefix log entries with current user's username.
  [zupo]


1.2 (2013-01-05)
----------------

- The ``product_id`` parameter is not always needed for in ``disable_member``
  so don't make it required.
  [zupo]

- The @@validity view now supports *dry-run* mode.
  [zupo]

- The @@validity view now prints processing results to the browser.
  [zupo]

- Better ``valid_to`` default value.
  [zupo]


1.1 (2013-01-02)
----------------

- Use ``ipn_`` as a prefix for product group IDs.
  [zupo]


1.0 (2012-12-27)
----------------

- Initial release.
  [zupo]

