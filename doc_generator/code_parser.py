"""
Code Parser

Parses .NET C# source code files and extracts relevant information
for documentation generation.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FileInfo:
    """Information about a parsed source file."""
    path: Path
    filename: str
    content: str
    relative_path: str
    
    # Extracted metadata
    namespace: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    

@dataclass
class ProjectInfo:
    """Information about a parsed project."""
    name: str
    path: Path
    files: List[FileInfo] = field(default_factory=list)
    
    @property
    def total_files(self) -> int:
        return len(self.files)
    
    @property
    def all_content(self) -> str:
        """Get concatenated content of all files."""
        return "\n\n".join([
            f"// File: {f.relative_path}\n{f.content}" 
            for f in self.files
        ])


class CodeParser:
    """Parses C# source code files from .NET projects."""
    
    # File patterns to include
    INCLUDE_PATTERNS = ["*.cs"]
    
    # Folders to exclude
    EXCLUDE_FOLDERS = [
        "bin", "obj", "Properties", "Migrations", 
        ".vs", "packages", "node_modules"
    ]
    
    # Files to exclude
    EXCLUDE_FILES = [
        "GlobalUsings.cs", 
        "AssemblyInfo.cs",
        ".Designer.cs"
    ]
    
    def __init__(self, project_root: Path):
        """
        Initialize the code parser.
        
        Args:
            project_root: Root directory of the project.
        """
        self.project_root = project_root
    
    def parse_project(self, project_path: Path) -> ProjectInfo:
        """
        Parse all C# files in a project directory.
        
        Args:
            project_path: Path to the project directory.
            
        Returns:
            ProjectInfo containing all parsed files.
        """
        project_name = project_path.name
        project_info = ProjectInfo(name=project_name, path=project_path)
        
        if not project_path.exists():
            print(f"Warning: Project path does not exist: {project_path}")
            return project_info
        
        # Find all .cs files
        for pattern in self.INCLUDE_PATTERNS:
            for file_path in project_path.rglob(pattern):
                # Skip excluded folders
                if any(excluded in file_path.parts for excluded in self.EXCLUDE_FOLDERS):
                    continue
                
                # Skip excluded files
                if any(file_path.name.endswith(excluded) for excluded in self.EXCLUDE_FILES):
                    continue
                
                # Parse the file
                file_info = self._parse_file(file_path, project_path)
                if file_info:
                    project_info.files.append(file_info)
        
        return project_info
    
    def parse_multiple_projects(self, project_paths: List[Path]) -> List[ProjectInfo]:
        """
        Parse multiple projects.
        
        Args:
            project_paths: List of project directory paths.
            
        Returns:
            List of ProjectInfo objects.
        """
        return [self.parse_project(path) for path in project_paths]
    
    def _parse_file(self, file_path: Path, project_path: Path) -> Optional[FileInfo]:
        """
        Parse a single C# file.
        
        Args:
            file_path: Path to the file.
            project_path: Path to the parent project.
            
        Returns:
            FileInfo object or None if file couldn't be parsed.
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read file {file_path}: {e}")
            return None
        
        relative_path = str(file_path.relative_to(project_path))
        
        file_info = FileInfo(
            path=file_path,
            filename=file_path.name,
            content=content,
            relative_path=relative_path
        )
        
        # Extract metadata
        file_info.namespace = self._extract_namespace(content)
        file_info.classes = self._extract_classes(content)
        file_info.interfaces = self._extract_interfaces(content)
        file_info.methods = self._extract_methods(content)
        
        return file_info
    
    def _extract_namespace(self, content: str) -> Optional[str]:
        """Extract namespace from C# code."""
        # Match both traditional and file-scoped namespaces
        match = re.search(r'namespace\s+([\w.]+)', content)
        return match.group(1) if match else None
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names from C# code."""
        pattern = r'(?:public|internal|private|protected)?\s*(?:static|abstract|sealed|partial)?\s*class\s+(\w+)'
        return re.findall(pattern, content)
    
    def _extract_interfaces(self, content: str) -> List[str]:
        """Extract interface names from C# code."""
        pattern = r'(?:public|internal|private|protected)?\s*interface\s+(I\w+)'
        return re.findall(pattern, content)
    
    def _extract_methods(self, content: str) -> List[str]:
        """Extract public method names from C# code."""
        pattern = r'public\s+(?:static\s+)?(?:async\s+)?(?:virtual\s+)?(?:override\s+)?[\w<>\[\],\s]+\s+(\w+)\s*\('
        return re.findall(pattern, content)
    
    def get_combined_content(self, projects: List[ProjectInfo], max_chars: int = 100000) -> str:
        """
        Get combined content from all projects, respecting token limits.
        
        Args:
            projects: List of parsed projects.
            max_chars: Maximum characters to include.
            
        Returns:
            Combined content string.
        """
        combined = []
        total_chars = 0
        
        for project in projects:
            project_header = f"\n{'='*60}\n# PROJECT: {project.name}\n{'='*60}\n"
            combined.append(project_header)
            total_chars += len(project_header)
            
            for file_info in project.files:
                file_header = f"\n// FILE: {file_info.relative_path}\n"
                file_content = file_info.content
                
                # Check if we're exceeding limit
                if total_chars + len(file_header) + len(file_content) > max_chars:
                    # Truncate or skip
                    remaining = max_chars - total_chars - len(file_header) - 100
                    if remaining > 500:
                        combined.append(file_header)
                        combined.append(file_content[:remaining])
                        combined.append("\n// ... (truncated for length)")
                    break
                
                combined.append(file_header)
                combined.append(file_content)
                total_chars += len(file_header) + len(file_content)
        
        return "".join(combined)
    
    def get_project_summary(self, projects: List[ProjectInfo]) -> Dict[str, Any]:
        """
        Get a summary of parsed projects.
        
        Args:
            projects: List of parsed projects.
            
        Returns:
            Dictionary with summary information.
        """
        summary = {
            "total_projects": len(projects),
            "total_files": sum(p.total_files for p in projects),
            "projects": []
        }
        
        for project in projects:
            project_summary = {
                "name": project.name,
                "files": project.total_files,
                "classes": [],
                "interfaces": [],
                "key_files": []
            }
            
            for file_info in project.files:
                project_summary["classes"].extend(file_info.classes)
                project_summary["interfaces"].extend(file_info.interfaces)
                
                # Identify key files
                if "Api" in file_info.filename or "Controller" in file_info.filename:
                    project_summary["key_files"].append(file_info.relative_path)
                elif "Command" in file_info.filename and "Handler" in file_info.filename:
                    project_summary["key_files"].append(file_info.relative_path)
            
            summary["projects"].append(project_summary)
        
        return summary
