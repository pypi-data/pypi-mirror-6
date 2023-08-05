"""
Representation of items in a Doorstop document.
"""

import os
import re
import functools
import logging

import yaml


from doorstop.common import DoorstopError


# http://en.wikipedia.org/wiki/Sentence_boundary_disambiguation
SBD = re.compile(r"((?<=[a-z0-9][.?!])|(?<=[a-z0-9][.?!]\"))(\s|\r\n)(?=\"?[A-Z])")  # pylint: disable=C0301


class _literal(str):  # pylint: disable=R0904
    """Custom type for text which should be dumped in the literal style."""
    pass


def _literal_representer(dumper, data):
    """Return a custom dumper that formats str in the literal style."""
    style = '|' if data else ''
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)

yaml.add_representer(_literal, _literal_representer)


def _auto_load(func):
    """Decorator for methods that should automatically load from file."""
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        """Wrapped method to call self.load() before execution."""
        self.load()
        if self.auto:
            return func(self, *args, **kwargs)
    return wrapped


def _auto_save(func):
    """Decorator for methods that should automatically save to file."""
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        """Wrapped method to call self.save() after execution."""
        result = func(self, *args, **kwargs)
        if self.auto:
            self.save()
        return result

    return wrapped


class Item(object):
    """Represents a file with linkable text that is part of a document."""

    EXTENSIONS = '.yml', '.yaml'

    DEFAULT_LEVEL = (1,)
    DEFAULT_TEXT = ""
    DEFAULT_REF = ""
    DEFAULT_LINKS = set()
    DEFAULT_NORMATIVE = True

    auto = True  # set to False to delay automatic load/save until load/save

    def __init__(self, path, root=os.getcwd()):
        """Load an item from an existing file.

        Internally, this constructor is also used to initialize new
        items by providing default properties.

        @param path: path to Item file
        @param root: path to root of project
        """
        # Check item's path
        if not os.path.isfile(path):
            raise DoorstopError("item does not exist: {}".format(path))
        # Check file name
        filename = os.path.basename(path)
        name, ext = os.path.splitext(filename)
        try:
            self.split_id(name)
        except DoorstopError:
            raise
        # Check file extension
        if ext.lower() not in self.EXTENSIONS:
            msg = "'{0}' extension not in {1}".format(path, self.EXTENSIONS)
            raise DoorstopError(msg)
        # Initialize Item
        self.path = path
        self.root = root
        self._exists = True
        self._level = Item.DEFAULT_LEVEL
        self._text = Item.DEFAULT_TEXT
        self._ref = Item.DEFAULT_REF
        self._links = Item.DEFAULT_LINKS
        self._normative = Item.DEFAULT_NORMATIVE
        self._data = {}

    def __repr__(self):
        return "Item({})".format(repr(self.path))

    def __str__(self):
        relpath = os.path.relpath(self.path, self.root)
        return "{} (@{}{})".format(self.id, os.sep, relpath)

    def __eq__(self, other):
        return isinstance(other, Item) and self.path == other.path

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.level < other.level

    @staticmethod
    def new(path, root, prefix, digits, number, level):  # pylint: disable=R0913
        """Create a new item.

        @param path: path to directory for the new item
        @param root: path to root of the project
        @param prefix: prefix for the new item
        @param digits: number of digits for the new document
        @param number: number for the new item
        @param level: level for the new item (None for default)

        @raise DoorstopError: if the item already exists
        """
        identifier = Item.join_id(prefix, digits, number)
        filename = identifier + Item.EXTENSIONS[0]
        path2 = os.path.join(path, filename)
        # Check for an existing item
        if os.path.exists(path2):
            raise DoorstopError("item already exists: {}".format(path2))
        # Create the item file
        Item._new(path2)
        # Return the new item
        item = Item(path2, root=root)
        item.level = level or Item.DEFAULT_LEVEL  # also saves the item
        return item

    @staticmethod
    def _new(path):  # pragma: no cover, integration test
        """Create a new item file.

        @param config: path to new item file
        """
        with open(path, 'w'):
            pass  # just touch the file

    def load(self, reload=False):
        """Load the item's properties from a file."""
        if getattr(self, '_loaded', False) and not reload:
            return
        logging.debug("loading {}...".format(repr(self)))
        # Read the YAML from file
        text = self._read()
        # Parse the YAML data
        try:
            self._data = yaml.load(text) or {}
        except yaml.scanner.ScannerError as error:  # pylint: disable=E1101
            msg = "invalid contents: {}:\n{}".format(self, error)
            raise DoorstopError(msg)
        # Store parsed data
        self._level = self._convert_level(self._data.get('level', self._level))
        self._text = self._data.get('text', self._text).strip()
        self._ref = self._data.get('ref', self._ref)
        self._links = set(self._data.get('links', self._links))
        self._normative = bool(self._data.get('normative', self._normative))
        # Set meta attributes
        setattr(self, '_loaded', True)
        self.auto = True

    def _read(self):  # pragma: no cover, integration test
        """Read text from the file."""
        if not self._exists:
            raise DoorstopError("cannot load from deleted: {}".format(self))
        with open(self.path, 'rb') as infile:
            return infile.read().decode('UTF-8')

    def save(self):
        """Format and save the item's properties to a file."""
        logging.debug("saving {}...".format(repr(self)))
        # Collect the data items
        level = '.'.join(str(n) for n in self._level)
        if len(self._level) == 2:
            level = float(level)
        elif len(self._level) == 1:
            level = int(level)
        text = _literal(self._sbd(self._text))
        ref = self._ref.strip()
        links = sorted(self._links)
        normative = self._normative
        # Build the data structure
        self._data['level'] = level
        self._data['text'] = text
        self._data['links'] = links
        self._data['ref'] = ref
        self._data['normative'] = normative
        # Dump the data to YAML
        dump = yaml.dump(self._data, default_flow_style=False)
        # Save the YAML to file
        self._write(dump)
        # Set meta attributes
        setattr(self, '_loaded', False)
        self.auto = True

    @staticmethod
    def _sbd(text):
        """Replace sentence boundaries with newlines and append a newline.

        >>> Item._sbd("Hello, world!")
        'Hello, world!\\n'

        >>> Item._sbd("Hello, world! How are you? I'm fine. Good.")
        "Hello, world!\\nHow are you?\\nI'm fine.\\nGood.\\n"

        """
        stripped = text.strip()
        if stripped:
            return SBD.sub('\n', stripped) + '\n'
        else:
            return ''

    def _write(self, text):  # pragma: no cover, integration test
        """Write text to the file."""
        if not self._exists:
            raise DoorstopError("cannot save to deleted: {}".format(self))
        with open(self.path, 'wb') as outfile:
            outfile.write(bytes(text, 'UTF-8'))

    @property
    def id(self):  # pylint: disable=C0103
        """Get the item's ID."""
        return os.path.splitext(os.path.basename(self.path))[0]

    @staticmethod
    def join_id(prefix, digits, number):
        """Join the parts of an item's ID into an ID.

        >>> Item.join_id('ABC', 5, 123)
        'ABC00123'

        """
        return "{}{}".format(prefix, str(number).zfill(digits))

    @staticmethod
    def split_id(text):
        """Split an item's ID into a prefix and number.

        >>> Item.split_id('ABC00123')
        ('ABC', 123)

        >>> Item.split_id('ABC.HLR_01-00123')
        ('ABC.HLR_01-', 123)

        """
        match = re.match(r"([\w.-]*\D)(\d+)", text)
        if not match:
            raise DoorstopError("invalid ID: {}".format(text))
        return match.group(1), int(match.group(2))

    @property
    def prefix(self):
        """Get the item ID's prefix."""
        return self.split_id(self.id)[0]

    @property
    def number(self):
        """Get the item ID's number."""
        return self.split_id(self.id)[1]

    @property
    @_auto_load
    def level(self):
        """Get the item level."""
        return self._level

    @level.setter
    @_auto_save
    def level(self, level):
        """Set the item's level."""
        self._level = self._convert_level(level)

    @property
    def heading(self):
        """Get the heading order based on the level."""
        level = list(self.level)
        while level[-1] == 0:
            del level[-1]
        return len(level)

    @staticmethod
    def _convert_level(text):
        """Convert a level string to a tuple.

        >>> Item._convert_level("1.2.3")
        (1, 2, 3)

        >>> Item._convert_level(['4', '5'])
        (4, 5)

        >>> Item._convert_level(4.2)
        (4, 2)

        """
        # Correct for integers (42) and floats (4.2) in YAML
        if isinstance(text, int) or isinstance(text, float):
            text = str(text)
        # Split strings by periods
        if isinstance(text, str):
            nums = text.split('.')
        else:
            nums = text
        return tuple(int(n) for n in nums)

    @property
    @_auto_load
    def text(self):
        """Get the item's text."""
        return self._text

    @text.setter
    @_auto_save
    def text(self, text):
        """Set the item's text."""
        self._text = text

    @property
    @_auto_load
    def ref(self):
        """Get the item's external file reference."""
        return self._ref

    @ref.setter
    @_auto_save
    def ref(self, ref):
        """Set the item's external file reference."""
        self._ref = ref

    @_auto_load
    def find_ref(self, root=None, ignored=None):
        """Find the external file reference and line number.

        @param root: override the path to the working copy (for testing)
        @param ignored: function to determine if a path should be skipped

        @return: relative path to file, line number (when found in file)
                 relative path to file, None (when found as filename)
                 None, None (when no ref)

        @raise DoorstopError: when no ref is found
        """
        if not self.ref:
            logging.debug("no external reference to search for")
            return None, None
        ignored = ignored or (lambda _: False)
        logging.info("seraching for ref '{}'...".format(self.ref))
        pattern = r"(\b|\W){}(\b|\W)".format(re.escape(self.ref))
        logging.debug("regex: {}".format(pattern))
        regex = re.compile(pattern)
        for root, _, filenames in os.walk(root or self.root):
            for filename in filenames:  # pragma: no cover, integration test
                path = os.path.join(root, filename)
                relpath = os.path.relpath(path, self.root)
                # Skip the item's file while searching
                if path == self.path:
                    continue
                # Skip hidden directories
                if (os.path.sep + '.') in path:
                    continue
                # Skip ignored paths
                if ignored(path):
                    continue
                # Search for the reference in the file
                if filename == self.ref:
                    return relpath, None
                try:
                    with open(path, 'r') as external:
                        for index, line in enumerate(external):
                            if regex.search(line):
                                logging.info("found ref: {}".format(relpath))
                                return relpath, index + 1
                except UnicodeDecodeError:
                    pass
        msg = "external reference not found: {}".format(self.ref)
        raise DoorstopError(msg)

    @property
    @_auto_load
    def links(self):
        """Get the items this item links to."""
        return sorted(self._links)

    @links.setter
    @_auto_save
    def links(self, links):
        """Set the items this item links to."""
        self._links = set(links)

    @property
    @_auto_load
    def normative(self):
        """Get the item's normative status."""
        return self._normative

    @normative.setter
    @_auto_save
    def normative(self, status):
        """Set the item's normative status."""
        self._normative = bool(status)

    @_auto_load
    @_auto_save
    def add_link(self, item):
        """Add a new link to another item."""
        self._links.add(item)

    @_auto_load
    @_auto_save
    def remove_link(self, item):
        """Remove an existing link."""
        try:
            self._links.remove(item)
        except KeyError:
            logging.warning("link to {0} does not exist".format(item))

    @_auto_load
    def get(self, name):
        """Get an extended attribute."""
        return self._data[name]

    @_auto_load
    @_auto_save
    def set(self, name, value):
        """SEt an extended attribute."""
        self._data[name] = value

    def check(self, document=None, tree=None, ignored=None):
        """Confirm the item is valid.

        @param document: document to validate the item
        @param tree: tree to validate the item
        @param ignored: function to determine if a path should be skipped

        @return: indication that the item is valid
        """
        logging.info("checking item {}...".format(self))
        # Verify the file can be parsed
        self.load()
        # Check text
        if not self.text and not self.ref:
            logging.warning("no text: {}".format(self))
        # Check external references
        self.find_ref(ignored=ignored)
        # Check links against the document
        if document:
            self._check_document(document)
        # Check links against the tree
        if tree:
            self._check_tree(tree)
        # Reformat the file
        self.save()
        # Item is valid
        return True

    def _check_document(self, document):
        """Check the item against its document."""
        # Verify an item has up links
        if document.parent and self.normative and not self.links:
            logging.warning("no links: {}".format(self))
        # Verify an item's links are to the correct parent
        for identifier in self.links:
            prefix = self.split_id(identifier)[0]
            if prefix.lower() != document.parent.lower():
                msg = "link to non-parent '{}' in {}".format(identifier, self)
                logging.warning(msg)

    def _check_tree(self, tree):
        """Check the item against the full tree."""
        # Verify an item's links are valid
        for identifier in self.links:
            item = tree.find_item(identifier)
            logging.debug("found linked item: {}".format(item))
        # Verify an item has down links
        for document in tree:
            if document.parent == self.prefix:
                links = []
                for item in document:
                    if self.id in item.links:
                        links.append(item.id)
                if links:
                    if self.normative:
                        msg = "down links: {}".format(', '.join(links))
                        logging.debug(msg)
                    else:
                        for link in links:
                            msg = "{} links to non-normative {}".format(link,
                                                                        self)
                            logging.warning(msg)
                elif self.normative:
                    msg = "{} has no links from {}".format(self, document)
                    logging.warning(msg)

    def delete(self):
        """Delete the item from the file system."""
        logging.info("deleting {}...".format(self.path))
        os.remove(self.path)
        self._exists = False  # prevent future access
