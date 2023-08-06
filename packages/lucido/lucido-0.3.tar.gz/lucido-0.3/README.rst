lucido
======

Ever wanted to release a project to the open source community, if only it weren't for the hassle of having to strip out sensitive data like API keys every time you commit?

Or maybe you've had to rewrite your version control history because you accidentally committed something that the rest of the world wasn't supposed to see?

**lucido** (pronounced loo-CHEE-dough) is a simple script designed to make these problems a thing of the past. On its own, it can strip and restore sensitive data with ease. Within a git repository, lucido prevents you from committing your sensitive data, and automatically restores it for you after any merges.

Installation
------------

From the command line::

    pip install lucido

If lucido is already installed, you can upgrade to the latest version with::

    pip install --upgrade lucido

You'll also need to have Perl installed [1]_. For most people, this shouldn't be an issue.

Getting Started
---------------

You'll want to create a file named ``luci.yml``. (If you're doing this within a git repository, make sure ``luci.yml`` is at the root of the repository.) It should contain, at the very least, a ``sensitive`` key, which will take a list of values that should be scrubbed by lucido.  It can also contain an ``exclude`` key, which can take a list of directories which should not be scrubbed.

Here's an example::

    exclude:
    - .git
    sensitive:
    - qqhPKzffeZu0
    - ALpeJmcMs7TG
    - z-1JWjRdbXzN
    - 3r_h1q_1TEs3

Note that you can also use regular expressions::

    exclude:
    - .git
    sensitive:
    - \w{12}

Usage
-----

If you plan to use lucido within a git repository, you'll only need to run the following::

    luci -i

This will create git hooks for you so that scrubbing/restoring is done automatically. (Technically, scrubbing is not automatic, as pre-commit hooks should not change the content of the files that are to be committed. But if sensitive data is found, the commit will fail and you'll be given a helpful message about how to scrub the data.)

If you're not using lucido within a git repository, you'll want to run these commands::

    # check for sensitive data
    luci -c
    # if present, scrub the sensitive data
    luci -s
    # at a later time, restore the sensitive data
    luci -r

Options
~~~~~~~

::

    -c, --check: Checks for sensitive data in the current working directory.
    -i, --init: Creates git hooks and adds luci.yml to .gitignore if run within a git repository.
    -s, --scrub: Scrubs sensitive data in the current working directory.
    -r, --restore: Restores sensitive data in the current working directory.

Git Hooks
---------

When initialized in a git repository, lucido adds the following git hooks:

* ``pre-commit``: Before committing, lucido will check the repository for sensitive data. If sensitive data is present, the commit will not be created.
* ``post-commit, post-merge``: After committing or merging in new changes, lucido will restore the sensitive data in your repository so that your code will work as expected.

Version Information
-------------------

Current stable release is v0.3, last updated on November 3, 2012.

Contributing
------------

Feel free to file any issues on the project's `bug tracker`_.

Or, if you're in a more philanthropic mood, consider leaving a `Gittip`_.

.. [1] lucido makes use of Perl in order to perform sed-like replacements in files. The reason sed itself isn't used is because it doesn't support literal (non-regex) search/replace, and juggling the escape characters is a circus feat I don't have the patience to perform.
.. _`bug tracker`: https://github.com/NSinopoli/lucido/issues
.. _`Gittip`: https://www.gittip.com/NSinopoli/
