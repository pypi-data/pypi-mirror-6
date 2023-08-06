
Changelog
---------

0.7 (2014-04-22)
~~~~~~~~~~~~~~~~

- Fixes exception being trigger if a private person is used in a published 
  membership. The membership is hidden now in this case. Fixes #17.
  [href]

- Show dates on organization view. Fixes #5.
  [href]

- Print numbers instead of stars for references in the report. Fixes #9.
  [href]

- Make email private. Fixes #10.
  [href]

- Remove reports from all organizations except the ones with the 'kommissionen'
  id. Fixes #11.
  [href]

- Fixes unicode decode error when editing memberships in organizations with
  titles outside the ASCII range. Closes #8.
  [href]

0.6 (2014-03-31)
~~~~~~~~~~~~~~~~

- Fixes critical error caused by a typo in the trigger-state view.
  [href]

0.5 (2014-03-31)
~~~~~~~~~~~~~~~~

- Adds start/end to Kantonsrat which hides them from the list of the people.
  [href]

- Adds the ability to define past, present and future memberships in 
  organizations.
  [href]

- Adds the ability to show external motions defined in
  https://github.com/4teamwork/geschaeftsverzeichnis.
  [href]

- Adds the ability to select a replacement for existing memberships.
  [href]

- Adds the ability to activate/deactivate organisations using a start/end date.
  Inactive organisations are not shown in the list and in the navigation. 
  They are still available through the url.

  This needs a cronjob run every night calling
  https://example.org/plone/trigger-state as administrator.
  [href]

- Adds the ability to directly edit the role and the note of a membership.
  Fixes #4.
  [href]

- Adds notes display to organization memberships.
  [href]

- Adds saner dateranges for birthday/entry date.
  [href]

- Adds a number of private fields for members.
  [href]

0.4 (2013-12-31)
~~~~~~~~~~~~~~~~

- Fixes more spelling errors. I can haz spell check?
  [href]

0.3 (2013-12-31)
~~~~~~~~~~~~~~~~

- Fixes really wrong spelling in German.
  [href]

0.2 (2013-12-31)
~~~~~~~~~~~~~~~~

- Adds parties, committees and factions. Fixes #1.
  [href]

0.1
~~~

- Initial release.
  [href]
