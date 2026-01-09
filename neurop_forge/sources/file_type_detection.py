"""
File Type Detection - Pure functions for identifying file types.

All functions are:
- Pure (no side effects, no filesystem access)
- Deterministic (same input = same output)
- Atomic (one intent per function)

Note: These functions work with file metadata (names, extensions, magic bytes)
without accessing the actual filesystem.

License: MIT
"""


def get_extension(filename: str) -> str:
    """Extract the file extension from a filename."""
    if not filename:
        return ""
    if '.' not in filename:
        return ""
    return filename.rsplit('.', 1)[-1].lower()


def get_extension_with_dot(filename: str) -> str:
    """Extract the file extension with leading dot."""
    ext = get_extension(filename)
    return f".{ext}" if ext else ""


def has_extension(filename: str, extension: str) -> bool:
    """Check if a filename has a specific extension."""
    return get_extension(filename) == extension.lower().lstrip('.')


def is_hidden_file(filename: str) -> bool:
    """Check if a filename represents a hidden file (starts with dot)."""
    if not filename:
        return False
    name = filename.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
    return name.startswith('.') and len(name) > 1


def get_file_category(extension: str) -> str:
    """Get the general category for a file extension."""
    extension = extension.lower().lstrip('.')
    categories = {
        "image": ["png", "jpg", "jpeg", "gif", "webp", "svg", "ico", "bmp", "tiff", "tif", "psd", "raw", "heic", "heif"],
        "video": ["mp4", "webm", "avi", "mov", "mkv", "flv", "wmv", "m4v", "mpeg", "mpg", "3gp"],
        "audio": ["mp3", "wav", "ogg", "flac", "aac", "wma", "m4a", "opus", "aiff"],
        "document": ["pdf", "doc", "docx", "odt", "rtf", "txt", "md", "tex", "epub", "mobi"],
        "spreadsheet": ["xls", "xlsx", "csv", "ods", "tsv"],
        "presentation": ["ppt", "pptx", "odp", "key"],
        "archive": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "tgz"],
        "code": ["py", "js", "ts", "jsx", "tsx", "java", "c", "cpp", "h", "hpp", "cs", "go", "rs", "rb", "php", "swift", "kt", "scala", "r", "lua", "pl", "sh", "bash", "zsh", "ps1"],
        "web": ["html", "htm", "css", "scss", "sass", "less", "vue", "svelte"],
        "data": ["json", "xml", "yaml", "yml", "toml", "ini", "cfg", "conf"],
        "font": ["ttf", "otf", "woff", "woff2", "eot"],
        "executable": ["exe", "msi", "dmg", "app", "deb", "rpm", "apk", "ipa"],
        "database": ["sql", "db", "sqlite", "sqlite3", "mdb", "accdb"],
    }
    for category, extensions in categories.items():
        if extension in extensions:
            return category
    return "other"


def is_image_extension(extension: str) -> bool:
    """Check if an extension represents an image file."""
    return get_file_category(extension) == "image"


def is_video_extension(extension: str) -> bool:
    """Check if an extension represents a video file."""
    return get_file_category(extension) == "video"


def is_audio_extension(extension: str) -> bool:
    """Check if an extension represents an audio file."""
    return get_file_category(extension) == "audio"


def is_document_extension(extension: str) -> bool:
    """Check if an extension represents a document file."""
    return get_file_category(extension) == "document"


def is_code_extension(extension: str) -> bool:
    """Check if an extension represents a code file."""
    return get_file_category(extension) == "code"


def is_archive_extension(extension: str) -> bool:
    """Check if an extension represents an archive file."""
    return get_file_category(extension) == "archive"


def is_web_extension(extension: str) -> bool:
    """Check if an extension represents a web file."""
    return get_file_category(extension) == "web"


def is_data_extension(extension: str) -> bool:
    """Check if an extension represents a data/config file."""
    return get_file_category(extension) == "data"


def is_media_extension(extension: str) -> bool:
    """Check if an extension represents any media file."""
    category = get_file_category(extension)
    return category in ("image", "video", "audio")


def is_text_based_extension(extension: str) -> bool:
    """Check if an extension represents a text-based file."""
    category = get_file_category(extension)
    return category in ("code", "web", "data", "document") or extension.lower().lstrip('.') in ("txt", "md", "csv", "log")


def get_language_for_extension(extension: str) -> str:
    """Get the programming language for a code file extension."""
    extension = extension.lower().lstrip('.')
    languages = {
        "py": "Python",
        "js": "JavaScript",
        "ts": "TypeScript",
        "jsx": "JavaScript (React)",
        "tsx": "TypeScript (React)",
        "java": "Java",
        "c": "C",
        "cpp": "C++",
        "h": "C Header",
        "hpp": "C++ Header",
        "cs": "C#",
        "go": "Go",
        "rs": "Rust",
        "rb": "Ruby",
        "php": "PHP",
        "swift": "Swift",
        "kt": "Kotlin",
        "scala": "Scala",
        "r": "R",
        "lua": "Lua",
        "pl": "Perl",
        "sh": "Shell",
        "bash": "Bash",
        "ps1": "PowerShell",
        "sql": "SQL",
        "html": "HTML",
        "css": "CSS",
        "scss": "SCSS",
        "sass": "Sass",
        "vue": "Vue",
        "svelte": "Svelte",
    }
    return languages.get(extension, "")


def detect_magic_bytes(header_bytes: bytes) -> str:
    """Detect file type from magic bytes (file header)."""
    if len(header_bytes) < 4:
        return "unknown"
    signatures = [
        (b'\x89PNG\r\n\x1a\n', "png"),
        (b'\xff\xd8\xff', "jpeg"),
        (b'GIF87a', "gif"),
        (b'GIF89a', "gif"),
        (b'RIFF', "wav"),
        (b'ID3', "mp3"),
        (b'\xff\xfb', "mp3"),
        (b'\xff\xfa', "mp3"),
        (b'OggS', "ogg"),
        (b'fLaC', "flac"),
        (b'%PDF', "pdf"),
        (b'PK\x03\x04', "zip"),
        (b'PK\x05\x06', "zip"),
        (b'Rar!\x1a\x07', "rar"),
        (b'\x1f\x8b', "gzip"),
        (b'BZh', "bzip2"),
        (b'\xfd7zXZ\x00', "xz"),
        (b'7z\xbc\xaf\x27\x1c', "7z"),
        (b'\x00\x00\x00\x1cftyp', "mp4"),
        (b'\x00\x00\x00\x20ftyp', "mp4"),
        (b'\x1aE\xdf\xa3', "webm"),
        (b'RIFF', "avi"),
        (b'MZ', "exe"),
        (b'\x7fELF', "elf"),
        (b'\xca\xfe\xba\xbe', "macho"),
        (b'\xfe\xed\xfa\xce', "macho"),
        (b'SQLite format 3', "sqlite"),
    ]
    for signature, file_type in signatures:
        if header_bytes.startswith(signature):
            return file_type
    if header_bytes[:4] == b'\x00\x00\x00\x0c' and header_bytes[4:8] == b'jP  ':
        return "jpeg2000"
    if header_bytes[:4] == b'WEBP' or (len(header_bytes) >= 12 and header_bytes[8:12] == b'WEBP'):
        return "webp"
    return "unknown"


def is_binary_extension(extension: str) -> bool:
    """Check if an extension typically represents a binary file."""
    extension = extension.lower().lstrip('.')
    binary_extensions = {
        "exe", "dll", "so", "dylib", "bin", "dat",
        "png", "jpg", "jpeg", "gif", "bmp", "ico", "webp", "tiff", "psd",
        "mp3", "wav", "ogg", "flac", "aac", "m4a",
        "mp4", "avi", "mkv", "mov", "webm", "flv",
        "zip", "rar", "7z", "tar", "gz", "bz2",
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
        "ttf", "otf", "woff", "woff2",
        "sqlite", "db", "mdb",
    }
    return extension in binary_extensions


def get_icon_name(extension: str) -> str:
    """Get a semantic icon name for a file extension."""
    category = get_file_category(extension)
    icon_map = {
        "image": "image",
        "video": "video",
        "audio": "audio",
        "document": "document",
        "spreadsheet": "table",
        "presentation": "presentation",
        "archive": "archive",
        "code": "code",
        "web": "globe",
        "data": "data",
        "font": "font",
        "executable": "application",
        "database": "database",
    }
    return icon_map.get(category, "file")


def is_safe_extension(extension: str) -> bool:
    """Check if a file extension is generally safe (not executable)."""
    extension = extension.lower().lstrip('.')
    unsafe_extensions = {
        "exe", "msi", "bat", "cmd", "com", "scr", "pif",
        "vbs", "vbe", "js", "jse", "ws", "wsf", "wsc", "wsh",
        "ps1", "psm1", "psd1",
        "sh", "bash", "zsh", "csh", "ksh",
        "app", "dmg", "pkg",
        "deb", "rpm", "apk",
        "jar", "war",
        "dll", "so", "dylib",
    }
    return extension not in unsafe_extensions


def get_compression_ratio_hint(extension: str) -> str:
    """Get a hint about expected compression for a file type."""
    extension = extension.lower().lstrip('.')
    already_compressed = {
        "jpg", "jpeg", "png", "gif", "webp",
        "mp3", "aac", "ogg", "flac",
        "mp4", "webm", "mkv", "avi",
        "zip", "rar", "7z", "gz", "bz2", "xz",
        "pdf", "docx", "xlsx", "pptx",
    }
    if extension in already_compressed:
        return "low"
    highly_compressible = {"txt", "log", "csv", "json", "xml", "html", "css", "js", "ts", "py", "java", "c", "cpp", "md"}
    if extension in highly_compressible:
        return "high"
    return "medium"


def normalize_extension(extension: str) -> str:
    """Normalize file extension to canonical form."""
    extension = extension.lower().lstrip('.')
    normalizations = {
        "jpeg": "jpg",
        "tiff": "tif",
        "htm": "html",
        "mpeg": "mpg",
        "yaml": "yml",
    }
    return normalizations.get(extension, extension)


def is_same_type(ext1: str, ext2: str) -> bool:
    """Check if two extensions represent the same file type."""
    return normalize_extension(ext1) == normalize_extension(ext2)


def get_default_application(extension: str) -> str:
    """Get a generic application type that opens this file type."""
    category = get_file_category(extension)
    app_map = {
        "image": "image_viewer",
        "video": "video_player",
        "audio": "audio_player",
        "document": "document_viewer",
        "spreadsheet": "spreadsheet_editor",
        "presentation": "presentation_viewer",
        "archive": "archive_manager",
        "code": "code_editor",
        "web": "web_browser",
        "data": "text_editor",
    }
    return app_map.get(category, "default")


def supports_preview(extension: str) -> bool:
    """Check if a file type typically supports preview."""
    extension = extension.lower().lstrip('.')
    previewable = {
        "png", "jpg", "jpeg", "gif", "webp", "svg", "bmp",
        "pdf", "txt", "md", "html", "htm",
        "json", "xml", "csv",
        "mp3", "wav", "ogg",
        "mp4", "webm",
    }
    return extension in previewable


def get_file_type_description(extension: str) -> str:
    """Get a human-readable description of the file type."""
    extension = extension.lower().lstrip('.')
    descriptions = {
        "png": "PNG Image",
        "jpg": "JPEG Image",
        "jpeg": "JPEG Image",
        "gif": "GIF Image",
        "webp": "WebP Image",
        "svg": "SVG Vector Image",
        "pdf": "PDF Document",
        "doc": "Word Document",
        "docx": "Word Document",
        "xls": "Excel Spreadsheet",
        "xlsx": "Excel Spreadsheet",
        "ppt": "PowerPoint Presentation",
        "pptx": "PowerPoint Presentation",
        "txt": "Plain Text File",
        "md": "Markdown Document",
        "json": "JSON Data File",
        "xml": "XML Data File",
        "csv": "CSV Spreadsheet",
        "zip": "ZIP Archive",
        "mp3": "MP3 Audio",
        "mp4": "MP4 Video",
        "py": "Python Script",
        "js": "JavaScript File",
        "html": "HTML Document",
        "css": "CSS Stylesheet",
    }
    if extension in descriptions:
        return descriptions[extension]
    category = get_file_category(extension)
    return f"{extension.upper()} {category.title()} File"
