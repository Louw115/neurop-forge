"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
File Path Utilities - Pure functions for path string manipulation.

Note: These functions work with path strings only, they do NOT access the filesystem.
This ensures they remain pure and deterministic.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def join_paths(path1: str, path2: str) -> str:
    """Join two path components with the appropriate separator."""
    if not path1:
        return path2
    if not path2:
        return path1
    if path1.endswith('/') or path1.endswith('\\'):
        return path1 + path2
    return path1 + '/' + path2


def get_filename(path: str) -> str:
    """Extract the filename from a path."""
    if not path:
        return ""
    path = path.replace('\\', '/')
    if '/' in path:
        return path.rsplit('/', 1)[-1]
    return path


def get_directory(path: str) -> str:
    """Extract the directory portion from a path."""
    if not path:
        return ""
    path = path.replace('\\', '/')
    if '/' in path:
        return path.rsplit('/', 1)[0]
    return ""


def get_extension(path: str) -> str:
    """Extract the file extension from a path."""
    filename = get_filename(path)
    if '.' not in filename:
        return ""
    return filename.rsplit('.', 1)[-1]


def get_extension_with_dot(path: str) -> str:
    """Extract the file extension from a path, including the dot."""
    ext = get_extension(path)
    if ext:
        return '.' + ext
    return ""


def get_basename(path: str) -> str:
    """Extract the filename without extension."""
    filename = get_filename(path)
    if '.' not in filename:
        return filename
    return filename.rsplit('.', 1)[0]


def change_extension(path: str, new_extension: str) -> str:
    """Change the file extension of a path."""
    if not path:
        return ""
    if new_extension and not new_extension.startswith('.'):
        new_extension = '.' + new_extension
    directory = get_directory(path)
    basename = get_basename(path)
    if directory:
        return directory + '/' + basename + new_extension
    return basename + new_extension


def normalize_path(path: str) -> str:
    """Normalize a path by converting backslashes to forward slashes."""
    return path.replace('\\', '/')


def normalize_path_windows(path: str) -> str:
    """Normalize a path by converting forward slashes to backslashes."""
    return path.replace('/', '\\')


def is_absolute_path(path: str) -> bool:
    """Check if a path is absolute."""
    if not path:
        return False
    if path.startswith('/'):
        return True
    if len(path) >= 2 and path[1] == ':':
        return True
    return False


def is_relative_path(path: str) -> bool:
    """Check if a path is relative."""
    return not is_absolute_path(path)


def has_extension(path: str, extension: str) -> bool:
    """Check if a path has a specific extension."""
    ext = get_extension(path).lower()
    check_ext = extension.lower().lstrip('.')
    return ext == check_ext


def split_path(path: str) -> list:
    """Split a path into its components."""
    if not path:
        return []
    normalized = normalize_path(path)
    parts = normalized.split('/')
    return [p for p in parts if p]


def get_parent_directory(path: str) -> str:
    """Get the parent directory of a path."""
    directory = get_directory(path)
    if directory:
        return get_directory(directory) or directory
    return ""


def add_trailing_slash(path: str) -> str:
    """Add a trailing slash to a path if not present."""
    if not path:
        return "/"
    if path.endswith('/') or path.endswith('\\'):
        return path
    return path + '/'


def remove_trailing_slash(path: str) -> str:
    """Remove a trailing slash from a path if present."""
    if not path:
        return ""
    while len(path) > 1 and (path.endswith('/') or path.endswith('\\')):
        path = path[:-1]
    return path


def is_hidden_file(path: str) -> bool:
    """Check if a file is hidden (starts with a dot)."""
    filename = get_filename(path)
    return filename.startswith('.') and len(filename) > 1


def get_depth(path: str) -> int:
    """Calculate the depth of a path (number of directory levels)."""
    parts = split_path(path)
    return len(parts)


def common_prefix(path1: str, path2: str) -> str:
    """Find the common path prefix of two paths."""
    parts1 = split_path(path1)
    parts2 = split_path(path2)
    common = []
    for p1, p2 in zip(parts1, parts2):
        if p1 == p2:
            common.append(p1)
        else:
            break
    return '/'.join(common)


def make_relative(path: str, base: str) -> str:
    """Make a path relative to a base path."""
    path_parts = split_path(path)
    base_parts = split_path(base)
    while path_parts and base_parts and path_parts[0] == base_parts[0]:
        path_parts.pop(0)
        base_parts.pop(0)
    up_count = len(base_parts)
    result_parts = ['..'] * up_count + path_parts
    return '/'.join(result_parts) if result_parts else '.'


def ensure_extension(path: str, extension: str) -> str:
    """Ensure a path has a specific extension."""
    if not extension.startswith('.'):
        extension = '.' + extension
    if path.lower().endswith(extension.lower()):
        return path
    return path + extension


def is_image_path(path: str) -> bool:
    """Check if a path points to a common image file."""
    ext = get_extension(path).lower()
    return ext in ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico')


def is_document_path(path: str) -> bool:
    """Check if a path points to a common document file."""
    ext = get_extension(path).lower()
    return ext in ('pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx')


def is_code_path(path: str) -> bool:
    """Check if a path points to a common source code file."""
    ext = get_extension(path).lower()
    return ext in ('py', 'js', 'ts', 'java', 'c', 'cpp', 'h', 'go', 'rs', 'rb', 'php', 'cs', 'swift', 'kt')


def is_archive_path(path: str) -> bool:
    """Check if a path points to a common archive file."""
    ext = get_extension(path).lower()
    return ext in ('zip', 'tar', 'gz', 'bz2', 'rar', '7z', 'xz')
