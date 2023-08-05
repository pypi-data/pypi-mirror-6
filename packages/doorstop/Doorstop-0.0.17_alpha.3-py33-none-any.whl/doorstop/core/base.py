"""
Classes and functions for objects whose attributes save to a file.
"""

import os
import abc
import functools
import logging

import yaml

from doorstop.common import DoorstopError


def auto_load(func):
    """Decorator for methods that should automatically load from file."""
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        """Wrapped method to call self.load() before execution."""
        self.load()
        return func(self, *args, **kwargs)
    return wrapped


def auto_save(func):
    """Decorator for methods that should automatically save to file."""
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        """Wrapped method to call self.save() after execution."""
        result = func(self, *args, **kwargs)
        if self.auto:
            self.save()
        return result

    return wrapped


class BaseFileObject(object, metaclass=abc.ABCMeta):  # pylint:disable=R0921
    """Abstract Base Class for objects whose attributes save to a file.

    For properties that are saved to a file, decorate their getters
    with @auto_load and their setters with @auto_save.
    """

    auto = True  # set to False to delay automatic save until explicit save

    def __init__(self):
        self._exists = True
        self._loaded = False

    @staticmethod
    def _new(path, name):  # pragma: no cover, integration test
        """Create a new file for the object.

        @param path: path to new file
        @param name: humanized name for this file

        @raise DoorstopError: if the file already exists
        """
        if os.path.exists(path):
            raise DoorstopError("{} already exists: {}".format(name, path))
        dirpath = os.path.dirname(path)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
        with open(path, 'w'):
            pass  # just touch the file

    @abc.abstractmethod
    def load(self, reload=False):  # pragma: no cover, abstract method
        """Load the object's properties from its file."""
        # Start implementations of this method with:
        if self._loaded and not reload:
            return
        # Call self._read() and update properties here:
        pass  # pylint: disable=W0107
        # End implementations of this method with:
        self._loaded = True

    def _read(self, path):  # pragma: no cover, integration test
        """Read text from the object's file."""
        if not self._exists:
            raise DoorstopError("cannot read from deleted: {}".format(self))
        with open(path, 'rb') as infile:
            return infile.read().decode('UTF-8')

    def _parse(self, text):
        """Load YAML data from text."""
        # Load the YAML data
        try:
            data = yaml.load(text) or {}
        except yaml.scanner.ScannerError as exc:  # pylint: disable=E1101
            # TODO: this is a hack -- Document can't be converted to string
            if hasattr(self, 'config'):
                path = getattr(self, 'config')
            else:
                path = getattr(self, 'path')
            msg = "invalid contents: {}:\n{}".format(path, exc)
            raise DoorstopError(msg) from None
        # Ensure data is a dictionary
        if not isinstance(data, dict):
            # TODO: this is a hack -- Document can't be converted to string
            if hasattr(self, 'config'):
                path = getattr(self, 'config')
            else:
                path = getattr(self, 'path')
            msg = "invalid contents: {}".format(path)
            raise DoorstopError(msg)
        return data

    @abc.abstractmethod
    def save(self):  # pragma: no cover, abstract method
        """Format and save the object's properties to its file."""
        # Call self._write() with the current properties here:
        pass  # pylint: disable=W0107
        # End implementations of this method with:
        self._loaded = False
        self.auto = True

    def _write(self, text, path):  # pragma: no cover, integration test
        """Write text to the object's file."""
        if not self._exists:
            raise DoorstopError("cannot save to deleted: {}".format(self))
        with open(path, 'wb') as outfile:
            outfile.write(bytes(text, 'UTF-8'))

    def delete(self, path):
        """Delete the object's file from the file system."""
        if self._exists:
            logging.info("deleting {}...".format(self))
            logging.debug("deleting file {}...".format(path))
            os.remove(path)
            self._loaded = False  # force the object to reload
            self._exists = False  # but, prevent future access
        else:
            logging.warning("already deleted: {}".format(self))
