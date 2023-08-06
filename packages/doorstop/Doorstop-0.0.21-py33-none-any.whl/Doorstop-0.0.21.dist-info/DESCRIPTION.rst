Introduction
============

Doorstop is a tool to manage the storage of textual requirements alongside
source code in version control.

Each requirement item is stored as a YAML file in a designated directory.
The items in each designated directory form a document. Document items can
be linked to one another to form a document hierarchy. Doorstop provides
mechanisms for modifying this hierarchy, checking the tree for consistency,
and publishing documents in several formats.

.. NOTE::
   0.0.x releases are experimental and interfaces will likely change.



Getting Started
===============

Requirements
------------

* Python 3.3
* Git or Veracity (for requirements storage)


Installation
------------

Doorstop can be installed with ``pip``::

    $ pip install Doorstop

After installation, Doorstop is available on the command-line::

    $ doorstop --help

And the package is available under the name ``doorstop``::

    $ python
    >>> import doorstop
    >>> doorstop.__version__


Document Creation
=================

Parent Document
---------------

After configuring version control, a new parent document can be created::

    $ doorstop new REQ ./reqs
    created document: REQ (@/reqs)

Items can be added to the document and edited::

    $ doorstop add REQ
    added item: REQ001 (@/reqs/REQ001.yml)

    $ doorstop edit REQ1
    opened item: REQ001 (@/reqs/REQ001.yml)


Child Documents
---------------

Additional documents can be created that link to other documents::

    $ doorstop new TST ./reqs/tests --parent REQ
    created document: TST (@/reqs/tests)

Items can be added and linked to parent items::

    $ doorstop add TST
    added item: TST001 (@/reqs/tests/TST001.yml)

    $ doorstop link TST1 REQ1
    linked item: TST001 (@/reqs/tests/TST001.yml) -> REQ001 (@/reqs/REQ001.yml)


Document Validation
===================

To check a document hierarchy for consistency, run the main command::

    $ doorstop
    valid tree: REQ <- [ TST ]


Document Publishing
===================

A text report of a document can be displayed::

    $ doorstop publish TST
    1       TST001

            Verify the foobar will foo and bar.

            Links: REQ001

Other formats are also supported::

    $ doorstop publish TST --html
    <!DOCTYPE html>
    ...
    <body>
    <h1>1 (TST001)</h1>
    <p>Verify the foobar will foo and bar.</p>
    <p><em>Links: REQ001</em></p>
    </body>
    </html>

Or a file can be created using one of the supported extensions::

   $ doorstop publish TST path/to/tst.md
   publishing TST to path/to/tst.md...

Supported formats:

* Text: **.txt**
* Markdown: **.md**
* HTML: **.html**

Changelog
=========

0.0.21 (2014/02/14)
-------------------

- Documents can now have Item files in sub-folders

0.0.20 (2014/02/13)
-------------------

- Updated doorstop.core.report to support lists of Items

0.0.19 (2014/02/13)
-------------------

- Updated doorstop.core.report to support Items or Documents
- Removed the 'iter\_' prefix from all generators

0.0.18 (2014/02/12)
-------------------

- Fixed CSS bullets indent

0.0.17 (2014/01/31)
-------------------

- Added caching of Items in the Document class
- Added Document.remove() to delete an item by its ID
- Item.find_rlinks() will now search the entire tree for links

0.0.16 (2014/01/28)
-------------------

- Added Item.find_rlinks() to return reverse links and child documents
- Changed the logging format
- Added a '--project' argument to provide a path to the root of the project


0.0.15 (2014/01/27)
-------------------

- Fixed a mutable default argument bug in Item creation

0.0.14 (2014/01/27)
--------------------

- Added Tree/Document/Item.iter_issues() method to yield all issues
- Tree/Document/Item.check() now logs all issues rather than failing fast
- Renamed Tree/Document/Item.check() to valid()

0.0.13 (2014/01/25)
-------------------

- Added Document.sep to separate prefix and item numbers.

0.0.12 (2014/01/24)
-------------------

- Fixed missing package data.

0.0.11 (2014/01/23)
-------------------

- Added Item.active property to disable certain items.
- Added Item.dervied property to disable link checking on certain items.

0.0.10 (2014/01/22)
-------------------

- Switched to embedded CSS in generated HTML.
- Shorted default Item and Document string formatting.

0.0.9 (2014/01/21)
------------------

- Added top-down link checking.
- Non-normative items with a zero-ended level are now headings.
- Added a CSS for generated HTML.
- The 'publish' command now accepts an output file path.

0.0.8 (2014/01/16)
------------------

- Searching for 'ref' will now also find filenames.
- Item files can now contain arbitrary fields.
- Document prefixes can now contain numbers, dashes, and periods.
- Added a 'normative' attribute to the Item class.

0.0.7 (2013/12/09)
------------------

- Always showing 'ref' in items.
- Reloading item attributes after a save.
- Inserting lines breaks after sentences in item 'text'.

0.0.6 (2013/12/04)
------------------

- Added basic report creation via 'doorstop publish'.

0.0.5 (2013/11/20)
------------------

- Added item link and reference validation.
- Added cached of loaded items.
- Added preliminary VCS support for Git and Veracity.

0.0.4 (2013/11/04)
------------------

- Implemented 'add', 'remove', 'link', and 'unlink' commands.
- Added basic tree validation.

0.0.3 (2013/10/17)
------------------

- Added the initial Document class.
- Items can now be ordered by 'level' in a Document.
- Initial tutorial created.

0.0.2 (2013/09/25)
------------------

- Changed 'doorstop init' to 'doorstop new'.
- Added the initial Item class.
- Added stubs for the Document class.

0.0.1 (2013/09/11)
------------------

- Initial release of Doorstop.


