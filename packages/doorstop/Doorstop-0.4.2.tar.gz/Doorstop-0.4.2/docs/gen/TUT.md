# 1.0 **Document and Item Creation**

## 1.1 TUT001

**Creating a new document and adding items.**

Enter VCS working copy:

    cd /tmp/doorstop

Create a new document:

    doorstop new REQ ./reqs

Add items:

    doorstop add REQ
    doorstop add REQ
    doorstop add REQ

Edit the new items in the default text editor:

    doorstop edit REQ1
    doorstop edit REQ2

*Links: REQ003, REQ004*

## 1.2 TUT002

**Creating a child document with links to the parent document.**

Enter VCS working copy:

    cd /tmp/doorstop

Create a new child document:

    doorstop new TST ./reqs/tests --parent REQ

Add new items:

    doorstop add TST
    doorstop add TST

Edit the new items in the default text editor:

    doorstop edit TST1
    doorstop edit TST2

Add links to item's in the parent document:

    doorstop link TST1 REQ1
    doorstop link TST1 REQ3
    doorstop link TST2 REQ1
    doorstop link TST2 REQ2

*Links: REQ003, REQ004, REQ011, REQ012, REQ013*

## 1.3 TUT004

**Removing items and links.**

Enter VCS working copy:

    cd /tmp/doorstop

Remove a link between two document items:

    doorstop unlink TST1 REQ3

Remove a document's item:

    doorstop remove REQ3

*Links: REQ003, REQ011, REQ012, REQ013*

## 1.4 TUT008

**Validating the tree.**

Enter VCS working copy:

    cd /tmp/doorstop

Build and validate the tree:

    doorstop

*Links: REQ003*

# 2.0 **Report Generation**

## 2.1 TUT009

**Creating a text report.**

Enter VCS working copy:

    cd /tmp/doorstop

Display the documents on standard output:

    doorstop publish req
    doorstop publish tst

*Links: REQ007*

