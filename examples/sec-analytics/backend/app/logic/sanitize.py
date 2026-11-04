"""Turn an untrusted filing document into plain text blocks (brief §7, M3-E2).

A filing is content from outside the app, so nothing active may reach the browser. This module
outputs only strings: no tag, attribute or link of the document survives. The browser then shows
each string as React text, so even a string that looks like markup stays words on the screen.

Parsed with BeautifulSoup's `html.parser` (standard library, no lxml). The rules:
- Removed with their contents: active and non-visible elements (`REMOVED_TAGS`), inline XBRL
  headers (hidden facts) and anything hidden with `display:none`, `visibility:hidden` or `hidden`.
- One block per paragraph-like element; one block per table row, with cells joined by " | " and
  empty cells dropped. A table holding long text is page layout, so it is read as paragraphs.
- Whitespace normalised; control, zero-width and text-direction characters removed.
- Blocks holding only a page number are dropped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from bs4 import BeautifulSoup
from bs4.element import NavigableString, PreformattedString, Tag

BlockKind = Literal["text", "heading", "table_row"]
MAX_BLOCKS = 30_000
MAX_TABLE_CELL_CHARS = 600

REMOVED_TAGS = (
    "script", "style", "noscript", "template", "iframe", "frame", "frameset", "object", "embed",
    "applet", "form", "input", "button", "select", "textarea", "svg", "math", "canvas", "audio",
    "video", "link", "meta", "base", "head", "title", "ix:header",
)
_REMOVED = frozenset(REMOVED_TAGS)
_BLOCK_TAGS = frozenset({
    "address", "article", "aside", "blockquote", "body", "caption", "center", "dd", "div", "dl",
    "dt", "figure", "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "html", "li",
    "main", "nav", "ol", "p", "pre", "section", "table", "tbody", "td", "tfoot", "th", "thead",
    "tr", "ul",
})
_HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
_HIDDEN_STYLE = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden", re.IGNORECASE)
_PAGE_NUMBER = re.compile(r"(?:[-–—]\s*)?(?:[A-Za-z]-)?[0-9]{1,4}(?:\s*[-–—])?")
# C0/C1 controls, zero-width characters, text-direction controls and the byte order mark.
_INVISIBLE = re.compile("[\x00-\x08\x0e-\x1f\x7f-\x9f​-‏‪-‮⁠-⁯﻿]")
_OPENS_NEXT_CELL = frozenset({"$", "€", "£", "(", "($", "(€", "(£"})
_CLOSES_LAST_CELL = frozenset({")", "%", ")%", "%)"})
_LOOKS_LIKE_HTML = re.compile(rb"<\s*(?:!doctype|html|body)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Block:
    """One piece of plain text from a document."""

    kind: BlockKind
    text: str


@dataclass(frozen=True)
class SanitizedDocument:
    """The blocks of a document. `truncated` says that the document was cut at `MAX_BLOCKS`."""

    blocks: list[Block]
    truncated: bool


def _decode(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def _clean(text: str) -> str:
    return " ".join(_INVISIBLE.sub("", text).split())


def _is_removed(tag: Tag) -> bool:
    if tag.name in _REMOVED or "hidden" in tag.attrs:
        return True
    style = tag.attrs.get("style")
    return isinstance(style, str) and _HIDDEN_STYLE.search(style) is not None


def _remove_non_visible(soup: BeautifulSoup) -> None:
    """One linear walk. BeautifulSoup's `find_all` slows down quadratically with nesting depth."""
    doomed: list[Tag] = []
    stack: list[Tag] = [soup]
    while stack:
        for child in stack.pop().children:
            if isinstance(child, Tag):
                (doomed if _is_removed(child) else stack).append(child)
    for tag in doomed:
        tag.decompose()


def _cells_text(cells: list[str]) -> str:
    """Join a row's cells, keeping `$` with its number and `)` or `%` with theirs."""
    joined: list[str] = []
    prefix = ""
    for cell in cells:
        if not cell:
            continue
        if cell in _OPENS_NEXT_CELL:
            prefix += cell
        elif cell in _CLOSES_LAST_CELL and joined and not prefix:
            joined[-1] += cell
        else:
            joined.append(prefix + cell)
            prefix = ""
    if prefix:
        joined.append(prefix)
    return " | ".join(joined)


def _has_stray_text(tag: Tag) -> bool:
    return any(
        isinstance(child, NavigableString)
        and not isinstance(child, PreformattedString)
        and child.strip()
        for child in tag.children
    )


def _row_text(row: Tag) -> str | None:
    """A row as text, or None when it cannot be flattened without losing or repeating text."""
    if _has_stray_text(row):
        return None
    cells: list[str] = []
    for child in row.children:
        if not isinstance(child, Tag):
            continue
        if child.name not in {"td", "th"}:
            if child.get_text().strip():
                return None
            continue
        if any(isinstance(d, Tag) and d.name == "table" for d in child.descendants):
            return None
        text = _clean(child.get_text())
        if len(text) > MAX_TABLE_CELL_CHARS:
            return None
        cells.append(text)
    return _cells_text(cells)


def _table_rows(table: Tag) -> list[str] | None:
    """The rows of a data table as text, or None when the table is page layout.

    A table inside a table, a cell of long text or an unusual structure means layout: the walker
    then reads it as ordinary blocks, so no text is lost or repeated.
    """
    rows: list[str] = []
    stack = [table]
    while stack:
        tag = stack.pop()
        if _has_stray_text(tag):
            return None
        sections: list[Tag] = []
        for child in tag.children:
            if not isinstance(child, Tag):
                continue
            if child.name == "tr":
                if sections:
                    return None  # rows both inside and outside thead/tbody: keep document order
                text = _row_text(child)
                if text is None:
                    return None
                rows.append(text)
            elif child.name in {"thead", "tbody", "tfoot"}:
                sections.append(child)
            elif child.get_text().strip():
                return None
        stack.extend(reversed(sections))
    return rows


class _Collector:
    """Collects blocks in document order, up to `MAX_BLOCKS`."""

    def __init__(self) -> None:
        self.blocks: list[Block] = []
        self.truncated = False

    def add(self, kind: BlockKind, text: str) -> None:
        if not text or (kind == "text" and _PAGE_NUMBER.fullmatch(text)):
            return
        if len(self.blocks) >= MAX_BLOCKS:
            self.truncated = True
            return
        self.blocks.append(Block(kind, text))


def _walk(soup: BeautifulSoup) -> SanitizedDocument:
    """Depth-first walk with an explicit stack, so a very deep document cannot overflow it."""
    out = _Collector()
    buffer: list[str] = []

    def flush(kind: BlockKind = "text") -> None:
        text = _clean("".join(buffer))
        buffer.clear()
        out.add(kind, text)

    stack: list[tuple[Tag, object]] = [(soup, iter(soup.children))]
    while stack:
        parent, children = stack[-1]
        node = next(children, None)
        if node is None:
            stack.pop()
            if parent.name in _BLOCK_TAGS:
                flush("heading" if parent.name in _HEADING_TAGS else "text")
            continue
        if isinstance(node, NavigableString):
            if not isinstance(node, PreformattedString):  # comments, doctype, CDATA and the like
                buffer.append(str(node))
            continue
        if not isinstance(node, Tag):
            continue
        if node.name == "br":
            buffer.append(" ")
            continue
        if node.name in _BLOCK_TAGS:
            flush()
        if node.name == "table":
            rows = _table_rows(node)
            if rows is not None:
                for row in rows:
                    out.add("table_row", row)
                continue
        stack.append((node, iter(node.children)))
    flush()
    return SanitizedDocument(out.blocks, out.truncated)


def html_to_blocks(raw: bytes) -> SanitizedDocument:
    """Sanitize an HTML document into plain text blocks."""
    soup = BeautifulSoup(_decode(raw), "html.parser")
    _remove_non_visible(soup)
    return _walk(soup)


def plain_text_to_blocks(raw: bytes) -> SanitizedDocument:
    """A plain text filing: one block per run of lines between blank lines."""
    out = _Collector()
    for paragraph in re.split(r"\r?\n\s*\r?\n", _decode(raw)):
        out.add("text", _clean(paragraph))
    return SanitizedDocument(out.blocks, out.truncated)


def to_blocks(raw: bytes, document_name: str) -> SanitizedDocument:
    """Choose the reader by the file name, trusting a `.txt` name only if the start is not HTML."""
    if document_name.lower().endswith(".txt") and not _LOOKS_LIKE_HTML.search(raw[:2048]):
        return plain_text_to_blocks(raw)
    return html_to_blocks(raw)
