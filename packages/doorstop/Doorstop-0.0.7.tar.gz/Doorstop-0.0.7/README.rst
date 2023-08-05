Introduction
============

Doorstop is a tool to manage the storage of texual requirements alongside
source code in version control.

Each requirement item is stored as a YAML file in a designated directory.
The items in each designated directory form a document. Document items can
be linked to one another to form a document hiearchy. Doorstop provides
mechanisms for modifying this hiearchy, checking the tree for consistency,
and publishing documents in serveral formats.

.. NOTE::
   0.0.x releases are experimental and interfaces will likely change.



Getting Started
===============

Requirements
------------

* Python 3
* Git or Veracity (for requirements storage)


Installation
------------

Doorstop can be installed with ``pip`` or ``easy_install``::

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
    created: REQ (@/reqs)

Items can be added to the document and edited::

    $ doorstop add REQ
    added: REQ001 (@/reqs/REQ001.yml)

    $ doorstop edit REQ1
    opened: REQ001 (@/reqs/REQ001.yml)


Child Documents
---------------

Additional documents can be created that link to other documents::

    $ doorstop new TST ./reqs/tests --parent REQ
    created: TST (@/reqs/tests)

Items can be added and linked to parent items::

    $ doorstop add TST
    added: TST001 (@/reqs/tests/TST001.yml)

    $ doorstop link TST1 REQ1
    linked: TST001 (@/reqs/tests/TST001.yml) -> REQ001 (@/reqs/REQ001.yml)


Document Validation
===================

To check a document hiearchy for consistency, run the main command::

    $ doorstop
    validated: REQ <- [ TST ]


Document Publishing
===================

A text report of a document can be created::

    $ doorstop publish TST
    1       TST001

            Verify the foobar will foo and bar.

            Links: REQ001

Other formats are also supported::

    $ doorstop publish TST --html
	<h1>1 (TST001)</h1>
	<p>Verify the foobar will foo and bar.</p>
	<p><em>Links: REQ001</em></p>
