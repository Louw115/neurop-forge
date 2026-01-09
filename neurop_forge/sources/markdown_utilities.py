"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Markdown Utilities - Pure functions for markdown parsing and manipulation.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import re


def escape_markdown(text: str) -> str:
    """Escape markdown special characters."""
    special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|']
    result = text
    for char in special_chars:
        result = result.replace(char, '\\' + char)
    return result


def unescape_markdown(text: str) -> str:
    """Remove markdown escape characters."""
    return re.sub(r'\\([\\`*_{}[\]()#+\-.!|])', r'\1', text)


def bold(text: str) -> str:
    """Wrap text in bold markdown."""
    return f"**{text}**"


def italic(text: str) -> str:
    """Wrap text in italic markdown."""
    return f"*{text}*"


def bold_italic(text: str) -> str:
    """Wrap text in bold italic markdown."""
    return f"***{text}***"


def strikethrough(text: str) -> str:
    """Wrap text in strikethrough markdown."""
    return f"~~{text}~~"


def inline_code(text: str) -> str:
    """Wrap text in inline code markdown."""
    if '`' in text:
        return f"``{text}``"
    return f"`{text}`"


def code_block(code: str, language: str) -> str:
    """Create a fenced code block."""
    return f"```{language}\n{code}\n```"


def link(text: str, url: str) -> str:
    """Create a markdown link."""
    return f"[{text}]({url})"


def link_with_title(text: str, url: str, title: str) -> str:
    """Create a markdown link with title."""
    return f'[{text}]({url} "{title}")'


def image(alt_text: str, url: str) -> str:
    """Create a markdown image."""
    return f"![{alt_text}]({url})"


def image_with_title(alt_text: str, url: str, title: str) -> str:
    """Create a markdown image with title."""
    return f'![{alt_text}]({url} "{title}")'


def heading(text: str, level: int) -> str:
    """Create a markdown heading."""
    level = max(1, min(6, level))
    return '#' * level + ' ' + text


def blockquote(text: str) -> str:
    """Create a markdown blockquote."""
    lines = text.split('\n')
    return '\n'.join('> ' + line for line in lines)


def horizontal_rule() -> str:
    """Create a horizontal rule."""
    return '---'


def unordered_list_item(text: str, indent: int) -> str:
    """Create an unordered list item."""
    return '  ' * indent + '- ' + text


def ordered_list_item(text: str, number: int, indent: int) -> str:
    """Create an ordered list item."""
    return '  ' * indent + f'{number}. ' + text


def task_list_item(text: str, checked: bool) -> str:
    """Create a task list item."""
    checkbox = '[x]' if checked else '[ ]'
    return f'- {checkbox} {text}'


def table_row(cells: list) -> str:
    """Create a markdown table row."""
    return '| ' + ' | '.join(str(cell) for cell in cells) + ' |'


def table_separator(num_columns: int) -> str:
    """Create a markdown table separator row."""
    return '| ' + ' | '.join(['---'] * num_columns) + ' |'


def table(headers: list, rows: list) -> str:
    """Create a complete markdown table."""
    lines = [table_row(headers), table_separator(len(headers))]
    for row in rows:
        lines.append(table_row(row))
    return '\n'.join(lines)


def extract_links(markdown: str) -> list:
    """Extract all links from markdown text."""
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return [{'text': m[0], 'url': m[1]} for m in re.findall(pattern, markdown)]


def extract_images(markdown: str) -> list:
    """Extract all images from markdown text."""
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return [{'alt': m[0], 'url': m[1]} for m in re.findall(pattern, markdown)]


def extract_headings(markdown: str) -> list:
    """Extract all headings from markdown text."""
    pattern = r'^(#{1,6})\s+(.+)$'
    return [{'level': len(m[0]), 'text': m[1].strip()} for m in re.findall(pattern, markdown, re.MULTILINE)]


def extract_code_blocks(markdown: str) -> list:
    """Extract all code blocks from markdown text."""
    pattern = r'```(\w*)\n(.*?)```'
    return [{'language': m[0], 'code': m[1]} for m in re.findall(pattern, markdown, re.DOTALL)]


def extract_inline_code(markdown: str) -> list:
    """Extract all inline code from markdown text."""
    pattern = r'`([^`]+)`'
    return re.findall(pattern, markdown)


def count_words(markdown: str) -> int:
    """Count words in markdown (excluding code and links)."""
    text = re.sub(r'```.*?```', '', markdown, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
    text = re.sub(r'[#*_~`\[\]()]', '', text)
    words = text.split()
    return len(words)


def strip_markdown(markdown: str) -> str:
    """Remove all markdown formatting, leaving plain text."""
    text = markdown
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    return text.strip()


def is_valid_link(text: str) -> bool:
    """Check if text is a valid markdown link."""
    pattern = r'^\[.+\]\(.+\)$'
    return bool(re.match(pattern, text))


def is_valid_image(text: str) -> bool:
    """Check if text is a valid markdown image."""
    pattern = r'^!\[.*\]\(.+\)$'
    return bool(re.match(pattern, text))


def get_heading_level(line: str) -> int:
    """Get the heading level of a line (0 if not a heading)."""
    match = re.match(r'^(#{1,6})\s', line)
    return len(match.group(1)) if match else 0


def increment_heading_level(markdown: str, increment: int) -> str:
    """Increment all heading levels in markdown."""
    def replace_heading(match):
        current_level = len(match.group(1))
        new_level = max(1, min(6, current_level + increment))
        return '#' * new_level + match.group(2)
    return re.sub(r'^(#{1,6})(\s+.+)$', replace_heading, markdown, flags=re.MULTILINE)


def convert_links_to_references(markdown: str) -> str:
    """Convert inline links to reference-style links."""
    links = extract_links(markdown)
    result = markdown
    references = []
    for i, link_data in enumerate(links, 1):
        ref_id = str(i)
        inline = f"[{link_data['text']}]({link_data['url']})"
        reference = f"[{link_data['text']}][{ref_id}]"
        result = result.replace(inline, reference, 1)
        references.append(f"[{ref_id}]: {link_data['url']}")
    if references:
        result += '\n\n' + '\n'.join(references)
    return result


def wrap_in_details(summary: str, content: str) -> str:
    """Create a collapsible details section."""
    return f"<details>\n<summary>{summary}</summary>\n\n{content}\n\n</details>"


def create_anchor(text: str) -> str:
    """Create a heading anchor from text."""
    anchor = text.lower()
    anchor = re.sub(r'[^\w\s-]', '', anchor)
    anchor = re.sub(r'[\s]+', '-', anchor)
    return anchor


def link_to_heading(text: str, heading_text: str) -> str:
    """Create a link to a heading."""
    anchor = create_anchor(heading_text)
    return f"[{text}](#{anchor})"


def generate_toc(markdown: str) -> str:
    """Generate a table of contents from headings."""
    headings = extract_headings(markdown)
    if not headings:
        return ""
    lines = ["## Table of Contents", ""]
    for h in headings:
        indent = "  " * (h['level'] - 1)
        anchor = create_anchor(h['text'])
        lines.append(f"{indent}- [{h['text']}](#{anchor})")
    return '\n'.join(lines)


def footnote(text: str, note_id: str) -> str:
    """Create a footnote reference."""
    return f"{text}[^{note_id}]"


def footnote_definition(note_id: str, content: str) -> str:
    """Create a footnote definition."""
    return f"[^{note_id}]: {content}"


def highlight(text: str) -> str:
    """Create highlighted text (if supported)."""
    return f"=={text}=="


def subscript(text: str) -> str:
    """Create subscript text (HTML)."""
    return f"<sub>{text}</sub>"


def superscript(text: str) -> str:
    """Create superscript text (HTML)."""
    return f"<sup>{text}</sup>"


def abbreviation(abbr: str, full: str) -> str:
    """Create an abbreviation definition."""
    return f"*[{abbr}]: {full}"


def definition_list_item(term: str, definition: str) -> str:
    """Create a definition list item."""
    return f"{term}\n: {definition}"


def split_frontmatter(markdown: str) -> dict:
    """Split YAML frontmatter from markdown content."""
    pattern = r'^---\n(.*?)\n---\n(.*)$'
    match = re.match(pattern, markdown, re.DOTALL)
    if match:
        return {'frontmatter': match.group(1), 'content': match.group(2)}
    return {'frontmatter': '', 'content': markdown}


def add_frontmatter(content: str, frontmatter: str) -> str:
    """Add YAML frontmatter to markdown content."""
    return f"---\n{frontmatter}\n---\n\n{content}"
