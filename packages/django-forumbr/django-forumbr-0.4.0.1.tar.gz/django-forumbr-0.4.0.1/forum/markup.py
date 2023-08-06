# -*- coding:utf-8 -*-

"""
Only bbcode is supported so far.
"""

from .constants import BBCODE, MARKDOWN, TEXTILE
from .constants import RST, PLAIN_HTML, PLAIN_TEXT

# FIXME: setup logging

try:
    import textile
except ImportError:
    textile = None
    print 'textile module not found. Textile support is off.'

try:
    import markdown
except ImportError:
    markdown = None
    print 'markdown module not found. Markdown support is off.'

try:
    import bbcode
except ImportError:
    bbcode = None
    print 'bbcode module not found. BBCode support is off.'

try:
    from docutils.core import publish_parts
except ImportError:
    publish_parts = None
    print 'docutils module not found. RST support is off.'

try:
    import html5lib
    from html5lib import sanitizer

    html_sanitizer = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
except ImportError:
    html_sanitizer = None
    print 'html5lib not found. Plain html support is off.'


def render_markup(markup, text):
    if text is None:
        return None

    if markup == BBCODE:
        if bbcode is not None:
            return bbcode.render_html(text)
    elif markup == MARKDOWN:
        if markdown is not None:
            return markdown.markdown(text)
    elif markup == TEXTILE:
        if textile is not None:
            return textile.textile(text)
    elif markup == RST:
        if publish_parts is not None:
            return publish_parts(text, writer_name='html')['fragment']
    elif markup == PLAIN_HTML:
        if html_sanitizer is not None:
            return html_sanitizer.parse(text)
    return text