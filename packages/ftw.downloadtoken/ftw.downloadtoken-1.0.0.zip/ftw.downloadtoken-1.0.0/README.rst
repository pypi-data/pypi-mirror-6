Introduction
============

``ftw.downloadtoken`` allows you to grant temporary access to a specific
downloadable content.

- You can send a email containing an url with a token to one or more recipients.

- Tokens are valid for 7 days.

- By default, ``ftw.downloadtoken`` works on ``File`` with the primaryField
  ``file``.

- Expired download tokens will be removed automatically on every new generated
  download token.


Installation
============

- Add ``ftw.downloadtoken`` to your buildout configuration:

::

    [instance]
    eggs +=
        ftw.downloadtoken

- Install the generic setup profile.



Usage
=====

Click the document action "Send download link".
Enter one or more email addresses.
Send link to recipients.



Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.1`, `4.2` or `4.3`.


Links
=====

- Main github project repository: https://github.com/4teamwork/ftw.downloadtoken
- Issue tracker: https://github.com/4teamwork/ftw.downloadtoken/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.downloadtoken
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.downloadtoken


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.downloadtoken`` is licensed under GNU General Public License, version 2.
