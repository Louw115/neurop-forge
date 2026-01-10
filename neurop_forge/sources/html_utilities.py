"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
HTML Utilities - Pure functions for HTML operations.
All functions are pure, deterministic, and atomic.
"""

import re


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;"))


def unescape_html(text: str) -> str:
    """Unescape HTML entities."""
    return (text
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'"))


def strip_tags(html: str) -> str:
    """Remove all HTML tags."""
    return re.sub(r'<[^>]+>', '', html)


def strip_tag(html: str, tag: str) -> str:
    """Remove specific HTML tag."""
    pattern = f'<{tag}[^>]*>.*?</{tag}>'
    return re.sub(pattern, '', html, flags=re.DOTALL | re.IGNORECASE)


def wrap_tag(content: str, tag: str) -> str:
    """Wrap content in tag."""
    return f"<{tag}>{content}</{tag}>"


def wrap_tag_with_attrs(content: str, tag: str, attrs: dict) -> str:
    """Wrap content in tag with attributes."""
    attr_str = " ".join(f'{k}="{escape_html(str(v))}"' for k, v in attrs.items())
    return f"<{tag} {attr_str}>{content}</{tag}>"


def create_element(tag: str, content: str, attrs: dict) -> str:
    """Create HTML element."""
    if attrs:
        attr_str = " ".join(f'{k}="{escape_html(str(v))}"' for k, v in attrs.items())
        return f"<{tag} {attr_str}>{content}</{tag}>"
    return f"<{tag}>{content}</{tag}>"


def create_void_element(tag: str, attrs: dict) -> str:
    """Create self-closing HTML element."""
    if attrs:
        attr_str = " ".join(f'{k}="{escape_html(str(v))}"' for k, v in attrs.items())
        return f"<{tag} {attr_str} />"
    return f"<{tag} />"


def create_link(href: str, text: str, new_tab: bool) -> str:
    """Create anchor link."""
    attrs = {"href": href}
    if new_tab:
        attrs["target"] = "_blank"
        attrs["rel"] = "noopener noreferrer"
    return create_element("a", escape_html(text), attrs)


def create_image(src: str, alt: str, width: int, height: int) -> str:
    """Create image element."""
    attrs = {"src": src, "alt": alt}
    if width:
        attrs["width"] = str(width)
    if height:
        attrs["height"] = str(height)
    return create_void_element("img", attrs)


def create_list(items: list, ordered: bool) -> str:
    """Create HTML list."""
    tag = "ol" if ordered else "ul"
    list_items = "".join(f"<li>{escape_html(str(item))}</li>" for item in items)
    return f"<{tag}>{list_items}</{tag}>"


def create_table(headers: list, rows: list) -> str:
    """Create HTML table."""
    thead = "<thead><tr>" + "".join(f"<th>{escape_html(str(h))}</th>" for h in headers) + "</tr></thead>"
    tbody_rows = ""
    for row in rows:
        tbody_rows += "<tr>" + "".join(f"<td>{escape_html(str(cell))}</td>" for cell in row) + "</tr>"
    tbody = f"<tbody>{tbody_rows}</tbody>"
    return f"<table>{thead}{tbody}</table>"


def create_input(input_type: str, name: str, value: str, attrs: dict) -> str:
    """Create input element."""
    all_attrs = {"type": input_type, "name": name, "value": value, **attrs}
    return create_void_element("input", all_attrs)


def create_select(name: str, options: list, selected: str) -> str:
    """Create select element."""
    opts = ""
    for opt in options:
        selected_attr = ' selected="selected"' if opt == selected else ""
        opts += f'<option value="{escape_html(str(opt))}"{selected_attr}>{escape_html(str(opt))}</option>'
    return f'<select name="{escape_html(name)}">{opts}</select>'


def extract_text(html: str) -> str:
    """Extract text content from HTML."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = strip_tags(text)
    return " ".join(text.split())


def extract_links(html: str) -> list:
    """Extract all links from HTML."""
    return re.findall(r'href=["\'](.*?)["\']', html)


def extract_images(html: str) -> list:
    """Extract all image sources from HTML."""
    return re.findall(r'src=["\'](.*?)["\']', html)


def minify_html(html: str) -> str:
    """Minify HTML by removing whitespace."""
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    html = re.sub(r'>\s+<', '><', html)
    html = re.sub(r'\s+', ' ', html)
    return html.strip()


def is_valid_tag(tag: str) -> bool:
    """Check if tag name is valid."""
    return bool(re.match(r'^[a-z][a-z0-9]*$', tag, re.IGNORECASE))


def add_class(attrs: dict, class_name: str) -> dict:
    """Add class to attributes."""
    result = dict(attrs)
    existing = result.get("class", "")
    if existing:
        result["class"] = f"{existing} {class_name}"
    else:
        result["class"] = class_name
    return result


def remove_class(attrs: dict, class_name: str) -> dict:
    """Remove class from attributes."""
    result = dict(attrs)
    existing = result.get("class", "")
    classes = [c for c in existing.split() if c != class_name]
    result["class"] = " ".join(classes)
    return result


def create_meta(name: str, content: str) -> str:
    """Create meta tag."""
    return create_void_element("meta", {"name": name, "content": content})


def create_comment(text: str) -> str:
    """Create HTML comment."""
    return f"<!-- {text} -->"
