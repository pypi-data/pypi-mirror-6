# -*- coding: utf8 -*-

"""Generate a clean nice starting html document to process for an article."""

from __future__ import absolute_import

import re
import logging
import charade

from lxml.etree import tostring, tounicode, XMLSyntaxError
from lxml.html import document_fromstring, HTMLParser

from ._compat import unicode, to_bytes, to_unicode, unicode_compatible
from .utils import cached_property


logger = logging.getLogger("breadability")


TAG_MARK_PATTERN = re.compile(to_bytes(r"</?[^>]*>\s*"))
def determine_encoding(page):
    encoding = "utf8"
    text = TAG_MARK_PATTERN.sub(to_bytes(" "), page)

    # don't venture to guess
    if not text.strip() or len(text) < 10:
        return encoding

    # try enforce UTF-8
    diff = text.decode(encoding, "ignore").encode(encoding)
    sizes = len(diff), len(text)

    # 99% of UTF-8
    if abs(len(text) - len(diff)) < max(sizes) * 0.01:
        return encoding

    # try detect encoding
    encoding_detector = charade.detect(text)
    if encoding_detector["encoding"]:
        encoding = encoding_detector["encoding"]

    return encoding


BREAK_TAGS_PATTERN = re.compile(to_unicode(r"(?:<\s*[bh]r[^>]*>\s*)+"), re.IGNORECASE)
def convert_breaks_to_paragraphs(html):
    """
    Converts <hr> tag and multiple <br> tags into paragraph.
    """
    logger.debug("Converting multiple <br> & <hr> tags into <p>.")

    return BREAK_TAGS_PATTERN.sub(_replace_break_tags, html)


def _replace_break_tags(match):
    tags = match.group()

    if to_unicode("<hr") in tags:
        return to_unicode("</p><p>")
    elif tags.count(to_unicode("<br")) > 1:
        return to_unicode("</p><p>")
    else:
        return tags


UTF8_PARSER = HTMLParser(encoding="utf8")
def build_document(html_content, base_href=None):
    """Requires that the `html_content` not be None"""
    assert html_content is not None

    if isinstance(html_content, unicode):
        html_content = html_content.encode("utf8", "replace")

    try:
        document = document_fromstring(html_content, parser=UTF8_PARSER)
    except XMLSyntaxError:
        raise ValueError("Failed to parse document contents.")

    if base_href:
        document.make_links_absolute(base_href, resolve_base_href=True)
    else:
        document.resolve_base_href()

    return document


@unicode_compatible
class OriginalDocument(object):
    """The original document to process."""

    def __init__(self, html, url=None):
        self._html = html
        self._url = url

    @property
    def url(self):
        """Source URL of HTML document."""
        return self._url

    def __unicode__(self):
        """Renders the document as a string."""
        return tounicode(self.dom)

    @cached_property
    def dom(self):
        """Parsed HTML document from the input."""
        html = self._html
        if not isinstance(html, unicode):
            encoding = determine_encoding(html)
            html = html.decode(encoding)

        html = convert_breaks_to_paragraphs(html)
        document = build_document(html, self._url)

        return document

    @cached_property
    def links(self):
        """Links within the document."""
        return self.dom.findall(".//a")

    @cached_property
    def title(self):
        """Title attribute of the parsed document."""
        title_element = self.dom.find(".//title")
        if title_element is None or title_element.text is None:
            return ""
        else:
            return title_element.text.strip()
