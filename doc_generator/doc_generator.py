"""
Documentation Generator

Generates structured documentation from parsed source code
using LLM analysis.
"""

import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .config_loader import ConfigLoader
from .code_parser import CodeParser, ProjectInfo
from .llm_adapter import BaseLLMAdapter, LLMFactory


class DocumentationGenerator:
    """Generates documentation from source code using LLM."""
    
    # System prompt for the LLM
    SYSTEM_PROMPT = """You are an expert technical documentation writer specializing in .NET microservices. 
Your task is to analyze source code and generate comprehensive, well-structured documentation.

Guidelines:
- Write clear, professional documentation
- Follow the exact structure provided in the template
- Include specific details from the code (class names, methods, endpoints)
- Create accurate Mermaid diagrams when requested
- Reference actual file paths from the source code
- Be thorough but concise"""

    def __init__(self, config: ConfigLoader):
        """
        Initialize the documentation generator.
        
        Args:
            config: Configuration loader.
        """
        self.config = config
        self.parser = CodeParser(config.project_root)
        self.llm: Optional[BaseLLMAdapter] = None
    
    def initialize_llm(self) -> None:
        """Initialize the LLM adapter."""
        self.llm = LLMFactory.create(self.config)
        print(f"Initialized LLM: {self.llm.get_model_name()}")
    
    def generate_documentation(self) -> str:
        """
        Generate documentation for configured source paths.
        
        Returns:
            Generated markdown documentation.
        """
        if not self.llm:
            self.initialize_llm()
        
        # Parse all projects
        print("Parsing source code...")
        projects = self.parser.parse_multiple_projects(self.config.source_paths)
        
        # Get summary for context
        summary = self.parser.get_project_summary(projects)
        print(f"Parsed {summary['total_files']} files from {summary['total_projects']} projects")
        
        # Get combined source code
        source_code = self.parser.get_combined_content(projects)
        
        # Generate documentation using LLM
        print("Generating documentation with LLM...")
        documentation = self._generate_with_llm(source_code, projects)
        
        return documentation
    
    def _generate_with_llm(self, source_code: str, projects: List[ProjectInfo]) -> str:
        """
        Generate documentation using the LLM.
        
        Args:
            source_code: Combined source code content.
            projects: List of parsed projects.
            
        Returns:
            Generated markdown documentation.
        """
        # Build the prompt
        prompt = self._build_prompt(source_code, projects)
        
        # Call LLM
        response = self.llm.generate(prompt, self.SYSTEM_PROMPT)
        
        return response
    
    def _build_prompt(self, source_code: str, projects: List[ProjectInfo]) -> str:
        """Build the documentation generation prompt."""
        
        project_names = [p.name for p in projects]
        include_diagrams = self.config.include_diagrams
        api_name = self.config.api_name
        
        prompt = f"""Analyze the following .NET source code and generate comprehensive API documentation for {api_name}.

## Projects to Document
{', '.join(project_names)}

## Documentation Template
Generate documentation with the following sections. Follow this structure exactly:

# [API Name] Documentation

## 1. Feature Overview
- Brief summary of what this API does
- Business motivation (3-4 bullet points)
- Key stakeholders (who uses this API)

## 2. Business Implementation Details
{"Include a Mermaid sequence diagram showing the main request flow." if include_diagrams else ""}
- Business rules implemented
- Use cases covered
- Assumptions and constraints

{"```mermaid" if include_diagrams else ""}
{"sequenceDiagram" if include_diagrams else ""}
{"    participant Client" if include_diagrams else ""}
{"    participant API" if include_diagrams else ""}
{"    ... (complete the diagram based on actual code flow)" if include_diagrams else ""}
{"```" if include_diagrams else ""}

## 3. Technical Implementation Details
{"Include a Mermaid class diagram showing key dependencies." if include_diagrams else ""}
- List all API endpoints with HTTP methods
- Key classes and their responsibilities
- Database/storage information
- Integration points with other services

## 4. Validation and Error Handling
- Input validation rules
- Error scenarios and HTTP status codes
- Retry/fallback logic

## 5. Security and Access Control
- Authentication mechanism
- Authorization rules
- Data access restrictions

## 6. Testing Strategy
- Types of tests (unit, integration, etc.)
- Key test scenarios
- Testing tools/frameworks used

## 7. Deployment Considerations
- Infrastructure requirements
- Configuration needed
- Post-deployment validation

## 8. References
- Links to key source files (use relative paths)
- Related documentation

---

## Source Code to Analyze

{source_code}

---

## Instructions
1. Analyze the source code thoroughly
2. Generate documentation following the template above
3. Include REAL class names, method names, and file paths from the code
4. For Mermaid diagrams, create accurate representations of the actual code flow
5. Be specific - reference actual implementations, not generic descriptions
6. Include all API endpoints found in the code
7. Document the CQRS pattern, domain events, and integration events if present

Generate the complete documentation now:"""

        return prompt
    
    def save_documentation(self, content: str, filename: Optional[str] = None) -> Path:
        """
        Save generated documentation to files.
        
        Args:
            content: Generated markdown content.
            filename: Output filename. If None, uses config.output_filename.
            
        Returns:
            Path to the saved file.
        """
        if filename is None:
            filename = self.config.output_filename
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Add generation metadata
        api_name = self.config.api_name
        metadata = f"""---
title: {api_name} Documentation
description: Auto-generated documentation for {api_name}
generated: {datetime.now().isoformat()}
generator: Automated Documentation Generator v1.0
---

"""
        full_content = metadata + content
        
        # Save to local_dev folder
        output_path = self.config.output_dir / filename
        output_path.write_text(full_content, encoding='utf-8')
        print(f"Saved to: {output_path}")
        
        # Copy to docs folder for MkDocs
        docs_path = self.config.docs_dir / filename
        shutil.copy(output_path, docs_path)
        print(f"Copied to: {docs_path}")
        
        # Update index.md to reflect the new documentation
        self._update_index_status(filename, api_name)
        
        return output_path
    
    def _update_index_status(self, filename: str, api_name: str) -> None:
        """
        Update the index.md file to show the API as documented.
        
        Args:
            filename: The documentation filename (e.g., 'ordering-api.md')
            api_name: The API name (e.g., 'Ordering API')
        """
        index_path = self.config.docs_dir / "index.md"
        
        if not index_path.exists():
            return
        
        try:
            content = index_path.read_text(encoding='utf-8')
            
            # Map of possible patterns to replace
            # Pattern: "| API Name | description | 🔄 Coming soon |" or placeholder status
            api_key = api_name.lower().replace(' api', '').strip()
            
            # Replace "Coming soon" with "Documented" for this API
            patterns = [
                (f"| {api_name} |", f"| [{api_name}]({filename}) |"),
                (f"🔄 Coming soon |", "✅ Documented |"),
                ("📄 Placeholder |", "✅ Documented |"),
            ]
            
            # More specific replacement based on API
            if "ordering" in api_key:
                content = content.replace(
                    "| Ordering API |",
                    f"| [Ordering API](ordering-api.md) |"
                )
            elif "catalog" in api_key:
                content = content.replace(
                    "| Catalog API |",
                    f"| [Catalog API](catalog-api.md) |"
                )
            elif "basket" in api_key:
                content = content.replace(
                    "| Basket API |",
                    f"| [Basket API](basket-api.md) |"
                )
            
            index_path.write_text(content, encoding='utf-8')
            print(f"Updated index.md status for {api_name}")
            
        except Exception as e:
            print(f"Warning: Could not update index.md: {e}")
    
    def run(self) -> Path:
        """
        Run the full documentation generation pipeline.
        
        Returns:
            Path to the generated documentation file.
        """
        print("=" * 60)
        print("AUTOMATED DOCUMENTATION GENERATOR")
        print("=" * 60)
        print()
        
        # Generate documentation
        documentation = self.generate_documentation()
        
        # Save documentation
        output_path = self.save_documentation(documentation)
        
        print()
        print("=" * 60)
        print("DOCUMENTATION GENERATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nOutput: {output_path}")
        print(f"\nTo view in browser:")
        print("  1. Run: mkdocs serve")
        print("  2. Open: http://127.0.0.1:8000")
        print()
        
        return output_path
