"""Shared data models for the documentation generator.

Design decision: Data classes are in a standalone module at the package
root so that every sub-package (parsing, generation, output) can import
them without circular dependencies. Keeping them separate from the
parsing logic that *populates* them follows the standard
data-vs-behaviour separation principle.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MethodInfo:
    """Parsed metadata for a single method declaration."""

    name: str
    line_number: int
    signature: str
    return_type: str
    parameters: List[Dict[str, str]]
    access_modifier: str
    is_async: bool
    body: str
    calls: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class PropertyInfo:
    """Parsed metadata for a single property or field."""

    name: str
    prop_type: str
    line_number: int
    access_modifier: str


@dataclass
class ClassInfo:
    """Parsed metadata for a single class or interface declaration."""

    name: str
    line_number: int
    kind: str                    # "class", "interface", "record", "enum"
    access_modifier: str
    base_class: Optional[str]
    interfaces: List[str]
    properties: List[PropertyInfo] = field(default_factory=list)
    methods: List[MethodInfo] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)


@dataclass
class FileInfo:
    """Parsed metadata for a single source file."""

    path: Path
    filename: str
    relative_path: str
    content: str
    namespace: Optional[str] = None
    classes: List[ClassInfo] = field(default_factory=list)
    category: str = "other"


@dataclass
class ProjectInfo:
    """Parsed metadata for a project directory."""

    name: str
    path: Path
    files: List[FileInfo] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        """Number of parsed files in this project."""
        return len(self.files)
