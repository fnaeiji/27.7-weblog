"""Shared utilities: slugification and Markdown sanitization."""

import re
import unicodedata

import bleach
from markdown_it import MarkdownIt

# Allowlist for rendered Markdown (research R3).
ALLOWED_TAGS = [
    'p',
    'br',
    'strong',
    'em',
    'u',
    's',
    'blockquote',
    'code',
    'pre',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'ul',
    'ol',
    'li',
    'dl',
    'dt',
    'dd',
    'a',
    'img',
    'table',
    'thead',
    'tbody',
    'tr',
    'th',
    'td',
    'hr',
    'div',
    'span',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'code': ['class'],
    'div': ['class'],
    'span': ['class'],
    '*': ['dir'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

_markdown = MarkdownIt('commonmark', {'html': False})
_non_word = re.compile(r'[^\w\s-]', re.UNICODE)


def slugify(value: object, allow_unicode: bool = True) -> str:
    """Return a URL-friendly slug, preserving Persian/Unicode letters."""
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = _non_word.sub('', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def sanitize_html(html: str) -> str:
    """Strip unsafe tags/attributes/protocols using the configured allowlist."""
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def markdown_to_safe_html(markdown_text: str) -> str:
    """Render Markdown to HTML and sanitize it (FR-023)."""
    raw_html = _markdown.render(markdown_text or '')
    return sanitize_html(raw_html)
