"""
Source code fetcher for GitHub repositories and local files.

This module provides secure, validated access to source code from:
- GitHub repositories (public)
- Local file system paths

All fetched code is validated for integrity and tracked for provenance.
"""

import os
import re
import hashlib
import urllib.request
import urllib.error
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SourceType(Enum):
    """Type of source location."""
    GITHUB = "github"
    LOCAL = "local"


class FetchStatus(Enum):
    """Status of a fetch operation."""
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ACCESS_DENIED = "access_denied"
    INVALID_PATH = "invalid_path"
    NETWORK_ERROR = "network_error"
    INVALID_CONTENT = "invalid_content"


@dataclass
class FetchResult:
    """Result of a source fetch operation."""
    status: FetchStatus
    source_type: SourceType
    path: str
    content: Optional[str]
    content_hash: Optional[str]
    file_size: int
    language: Optional[str]
    error_message: Optional[str]
    metadata: Dict[str, Any]

    def is_success(self) -> bool:
        return self.status == FetchStatus.SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "source_type": self.source_type.value,
            "path": self.path,
            "content_hash": self.content_hash,
            "file_size": self.file_size,
            "language": self.language,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class SourceFetcher:
    """
    Fetches source code from various locations with validation.
    
    Features:
    - GitHub raw file fetching
    - Local file system access
    - Content integrity verification
    - Language detection
    - Size limits enforcement
    """

    SUPPORTED_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".mjs": "javascript",
        ".cjs": "javascript",
    }

    MAX_FILE_SIZE = 1024 * 1024  # 1MB limit

    GITHUB_RAW_URL_PATTERN = re.compile(
        r"^https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$"
    )

    def __init__(
        self,
        allowed_extensions: Optional[List[str]] = None,
        max_file_size: Optional[int] = None,
    ):
        self._allowed_extensions = allowed_extensions or list(self.SUPPORTED_EXTENSIONS.keys())
        self._max_file_size = max_file_size or self.MAX_FILE_SIZE

    def fetch_local(self, path: str) -> FetchResult:
        """
        Fetch source code from local file system.
        
        Args:
            path: Path to the local file
            
        Returns:
            FetchResult: The result of the fetch operation
        """
        file_path = Path(path)

        if not file_path.exists():
            return FetchResult(
                status=FetchStatus.NOT_FOUND,
                source_type=SourceType.LOCAL,
                path=path,
                content=None,
                content_hash=None,
                file_size=0,
                language=None,
                error_message=f"File not found: {path}",
                metadata={},
            )

        if not file_path.is_file():
            return FetchResult(
                status=FetchStatus.INVALID_PATH,
                source_type=SourceType.LOCAL,
                path=path,
                content=None,
                content_hash=None,
                file_size=0,
                language=None,
                error_message=f"Path is not a file: {path}",
                metadata={},
            )

        extension = file_path.suffix.lower()
        if extension not in self._allowed_extensions:
            return FetchResult(
                status=FetchStatus.INVALID_CONTENT,
                source_type=SourceType.LOCAL,
                path=path,
                content=None,
                content_hash=None,
                file_size=0,
                language=None,
                error_message=f"Unsupported file extension: {extension}",
                metadata={},
            )

        file_size = file_path.stat().st_size
        if file_size > self._max_file_size:
            return FetchResult(
                status=FetchStatus.INVALID_CONTENT,
                source_type=SourceType.LOCAL,
                path=path,
                content=None,
                content_hash=None,
                file_size=file_size,
                language=None,
                error_message=f"File too large: {file_size} bytes (max: {self._max_file_size})",
                metadata={},
            )

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            return FetchResult(
                status=FetchStatus.INVALID_CONTENT,
                source_type=SourceType.LOCAL,
                path=path,
                content=None,
                content_hash=None,
                file_size=file_size,
                language=None,
                error_message=f"Cannot decode file as UTF-8: {e}",
                metadata={},
            )

        content_hash = hashlib.sha256(content.encode()).hexdigest()
        language = self.SUPPORTED_EXTENSIONS.get(extension)

        return FetchResult(
            status=FetchStatus.SUCCESS,
            source_type=SourceType.LOCAL,
            path=str(file_path.absolute()),
            content=content,
            content_hash=content_hash,
            file_size=len(content),
            language=language,
            error_message=None,
            metadata={
                "filename": file_path.name,
                "extension": extension,
                "absolute_path": str(file_path.absolute()),
            },
        )

    def fetch_github(self, url: str) -> FetchResult:
        """
        Fetch source code from GitHub.
        
        Args:
            url: GitHub blob URL (e.g., https://github.com/owner/repo/blob/main/file.py)
            
        Returns:
            FetchResult: The result of the fetch operation
        """
        match = self.GITHUB_RAW_URL_PATTERN.match(url)
        if not match:
            return FetchResult(
                status=FetchStatus.INVALID_PATH,
                source_type=SourceType.GITHUB,
                path=url,
                content=None,
                content_hash=None,
                file_size=0,
                language=None,
                error_message="Invalid GitHub URL format",
                metadata={},
            )

        owner, repo, branch, file_path = match.groups()
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"

        extension = Path(file_path).suffix.lower()
        if extension not in self._allowed_extensions:
            return FetchResult(
                status=FetchStatus.INVALID_CONTENT,
                source_type=SourceType.GITHUB,
                path=url,
                content=None,
                content_hash=None,
                file_size=0,
                language=None,
                error_message=f"Unsupported file extension: {extension}",
                metadata={},
            )

        try:
            with urllib.request.urlopen(raw_url, timeout=30) as response:
                content_bytes = response.read()

                if len(content_bytes) > self._max_file_size:
                    return FetchResult(
                        status=FetchStatus.INVALID_CONTENT,
                        source_type=SourceType.GITHUB,
                        path=url,
                        content=None,
                        content_hash=None,
                        file_size=len(content_bytes),
                        language=None,
                        error_message=f"File too large: {len(content_bytes)} bytes",
                        metadata={},
                    )

                content = content_bytes.decode("utf-8")

        except urllib.error.HTTPError as e:
            if e.code == 404:
                status = FetchStatus.NOT_FOUND
            elif e.code == 403:
                status = FetchStatus.ACCESS_DENIED
            else:
                status = FetchStatus.NETWORK_ERROR

            return FetchResult(
                status=status,
                source_type=SourceType.GITHUB,
                path=url,
                content=None,
                content_hash=None,
                file_size=0,
                language=None,
                error_message=f"HTTP error {e.code}: {e.reason}",
                metadata={},
            )
        except urllib.error.URLError as e:
            return FetchResult(
                status=FetchStatus.NETWORK_ERROR,
                source_type=SourceType.GITHUB,
                path=url,
                content=None,
                content_hash=None,
                file_size=0,
                language=None,
                error_message=f"Network error: {e.reason}",
                metadata={},
            )

        content_hash = hashlib.sha256(content.encode()).hexdigest()
        language = self.SUPPORTED_EXTENSIONS.get(extension)

        return FetchResult(
            status=FetchStatus.SUCCESS,
            source_type=SourceType.GITHUB,
            path=url,
            content=content,
            content_hash=content_hash,
            file_size=len(content),
            language=language,
            error_message=None,
            metadata={
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "file_path": file_path,
                "raw_url": raw_url,
            },
        )

    def fetch(self, source: str) -> FetchResult:
        """
        Fetch source code from either GitHub or local file system.
        
        Args:
            source: Either a GitHub URL or local file path
            
        Returns:
            FetchResult: The result of the fetch operation
        """
        if source.startswith("https://github.com/"):
            return self.fetch_github(source)
        else:
            return self.fetch_local(source)

    def fetch_directory(self, directory: str) -> List[FetchResult]:
        """
        Fetch all supported source files from a directory.
        
        Args:
            directory: Path to the directory
            
        Returns:
            List[FetchResult]: Results for each file
        """
        results = []
        dir_path = Path(directory)

        if not dir_path.exists() or not dir_path.is_dir():
            return results

        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                extension = file_path.suffix.lower()
                if extension in self._allowed_extensions:
                    result = self.fetch_local(str(file_path))
                    results.append(result)

        return results

    def detect_language(self, path: str) -> Optional[str]:
        """Detect the programming language from file extension."""
        extension = Path(path).suffix.lower()
        return self.SUPPORTED_EXTENSIONS.get(extension)
