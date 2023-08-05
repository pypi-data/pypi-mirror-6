"""
Doorstop reporting functionality.
"""

import os
import textwrap
import markdown


def get_text(document, indent=8, width=79, ignored=None):
    """Yield lines for a text report.

    @param document: Document to publish
    @param indent: number of spaces to indent text
    @param width: maximum line length
    @param ignored: function to determine if a path should be skipped

    @return: iterator of lines of text
    """
    for item in document.items:

        level = '.'.join(str(l) for l in item.level)
        identifier = item.id

        # Level and ID
        yield "{l:<{s}}{i}".format(l=level, i=identifier, s=indent)

        # Text
        if item.text:
            yield ""  # break before text
            for line in item.text.splitlines():
                for chunk in _chunks(line, width, indent):
                    yield chunk

                if not line:  # pragma: no cover - integration test
                    yield ""  # break between paragraphs

        # Reference
        if item.ref:
            yield ""  # break before reference
            path, line = item.find_ref(ignored=ignored)
            relpath = os.path.relpath(path, item.root).replace('\\', '/')
            ref = "Reference: {p} (line {l})".format(p=relpath, l=line)
            for chunk in _chunks(ref, width, indent):
                yield chunk

        # Links
        if item.links:
            yield ""  # break before links
            links = "Links: " + ', '.join(item.links)
            for chunk in _chunks(links, width, indent):
                yield chunk

        yield ""  # break between items


def _chunks(text, width, indent):
    """Yield wrapped lines of text."""
    for chunk in textwrap.wrap(text, width,
                               initial_indent=' ' * indent,
                               subsequent_indent=' ' * indent):
        yield chunk


def get_markdown(document, ignored=None):
    """Yield lines for a Markdown report.

    @param document: Document to publish
    @param ignored: function to determine if a path should be skipped

    @return: iterator of lines of text
    """
    for item in document.items:

        heading = '#' * item.heading
        level = '.'.join(str(l) for l in item.level)
        identifier = item.id

        # Level and ID
        yield "{h} {l} ({i})".format(h=heading, l=level, i=identifier)

        # Text
        if item.text:
            yield ""  # break before text
            for line in item.text.splitlines():
                yield line

        # Reference
        if item.ref:
            yield ""  # break before reference
            path, line = item.find_ref(ignored=ignored)
            relpath = os.path.relpath(path, item.root).replace('\\', '/')
            ref = "Reference: {p} (line {l})".format(p=relpath, l=line)
            yield ref

        # Links
        if item.links:
            yield ""  # break before links
            links = '*' + "Links: " + ', '.join(item.links) + '*'
            yield links

        yield ""  # break between items


def get_html(document, ignored=None):
    """Yield lines for an HTML report.

    @param document: Document to publish
    @param ignored: function to determine if a path should be skipped

    @return: iterator of lines of text
    """
    lines = get_markdown(document, ignored=ignored)
    text = '\n'.join(lines)
    html = markdown.markdown(text)
    for line in html.splitlines():
        yield line
