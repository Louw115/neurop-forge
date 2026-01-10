"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Template Utilities - Pure functions for template processing.
All functions are pure, deterministic, and atomic.
"""

def interpolate_template(template: str, variables: dict) -> str:
    """Interpolate variables into template."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def interpolate_double_braces(template: str, variables: dict) -> str:
    """Interpolate using double brace syntax {{key}}."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def find_template_variables(template: str) -> list:
    """Find all variable placeholders in template."""
    import re
    return re.findall(r'\{(\w+)\}', template)


def find_missing_variables(template: str, provided: dict) -> list:
    """Find variables in template not provided in dictionary."""
    required = set(find_template_variables(template))
    return list(required - set(provided.keys()))


def has_all_variables(template: str, provided: dict) -> bool:
    """Check if all template variables are provided."""
    return len(find_missing_variables(template, provided)) == 0


def escape_template_syntax(text: str) -> str:
    """Escape template syntax in text."""
    return text.replace("{", "{{").replace("}", "}}")


def unescape_template_syntax(text: str) -> str:
    """Unescape template syntax in text."""
    return text.replace("{{", "{").replace("}}", "}")


def build_conditional_block(condition_name: str, content: str) -> str:
    """Build a conditional template block."""
    return f"{{%if {condition_name}%}}{content}{{%endif%}}"


def build_loop_block(item_name: str, collection_name: str, content: str) -> str:
    """Build a loop template block."""
    return f"{{%for {item_name} in {collection_name}%}}{content}{{%endfor%}}"


def build_partial_include(partial_name: str) -> str:
    """Build a partial include statement."""
    return f"{{%include '{partial_name}'%}}"


def extract_front_matter(content: str) -> dict:
    """Extract YAML front matter from template."""
    if not content.startswith("---"):
        return {"frontmatter": {}, "content": content}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"frontmatter": {}, "content": content}
    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    return {"frontmatter": frontmatter, "content": parts[2].strip()}


def apply_default_values(variables: dict, defaults: dict) -> dict:
    """Apply default values for missing variables."""
    result = dict(defaults)
    result.update(variables)
    return result


def format_template_error(template_name: str, line: int, error: str) -> str:
    """Format a template error message."""
    return f"Template '{template_name}' error at line {line}: {error}"


def validate_template_syntax(template: str) -> dict:
    """Validate template syntax (basic checks)."""
    errors = []
    open_braces = template.count("{")
    close_braces = template.count("}")
    if open_braces != close_braces:
        errors.append("Mismatched braces")
    return {"valid": len(errors) == 0, "errors": errors}


def strip_template_comments(template: str) -> str:
    """Remove template comments."""
    import re
    return re.sub(r'\{#.*?#\}', '', template, flags=re.DOTALL)


def minify_template(template: str) -> str:
    """Minify template by removing extra whitespace."""
    import re
    result = strip_template_comments(template)
    result = re.sub(r'\s+', ' ', result)
    return result.strip()


def build_template_context(base_context: dict, page_context: dict) -> dict:
    """Build merged template context."""
    return {**base_context, **page_context}


def format_as_html_list(items: list, list_type: str) -> str:
    """Format items as HTML list."""
    tag = "ol" if list_type == "ordered" else "ul"
    items_html = "".join(f"<li>{item}</li>" for item in items)
    return f"<{tag}>{items_html}</{tag}>"


def format_as_table(rows: list, headers: list) -> str:
    """Format data as HTML table."""
    header_html = "".join(f"<th>{h}</th>" for h in headers)
    rows_html = ""
    for row in rows:
        cells = "".join(f"<td>{cell}</td>" for cell in row)
        rows_html += f"<tr>{cells}</tr>"
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{rows_html}</tbody></table>"


def build_select_options(options: list, selected: str) -> str:
    """Build HTML select options."""
    result = []
    for opt in options:
        value = opt if isinstance(opt, str) else opt.get("value", "")
        label = opt if isinstance(opt, str) else opt.get("label", value)
        selected_attr = ' selected' if value == selected else ''
        result.append(f'<option value="{value}"{selected_attr}>{label}</option>')
    return "".join(result)


def build_radio_buttons(name: str, options: list, selected: str) -> str:
    """Build HTML radio buttons."""
    result = []
    for opt in options:
        value = opt if isinstance(opt, str) else opt.get("value", "")
        label = opt if isinstance(opt, str) else opt.get("label", value)
        checked = ' checked' if value == selected else ''
        result.append(f'<label><input type="radio" name="{name}" value="{value}"{checked}> {label}</label>')
    return "".join(result)


def build_checkbox_group(name: str, options: list, selected: list) -> str:
    """Build HTML checkbox group."""
    result = []
    for opt in options:
        value = opt if isinstance(opt, str) else opt.get("value", "")
        label = opt if isinstance(opt, str) else opt.get("label", value)
        checked = ' checked' if value in selected else ''
        result.append(f'<label><input type="checkbox" name="{name}[]" value="{value}"{checked}> {label}</label>')
    return "".join(result)


def paginate_template_data(items: list, page: int, per_page: int) -> dict:
    """Paginate data for template."""
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages
    }


def build_breadcrumbs(path_segments: list, base_url: str) -> list:
    """Build breadcrumb navigation data."""
    breadcrumbs = [{"label": "Home", "url": base_url}]
    current_path = base_url
    for segment in path_segments:
        current_path = f"{current_path}/{segment}"
        breadcrumbs.append({"label": segment.replace("-", " ").title(), "url": current_path})
    return breadcrumbs
