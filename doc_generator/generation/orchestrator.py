"""Documentation generation orchestrator.

Design decision: This module coordinates the full pipeline --
parse -> classify -> generate -> assemble -- making targeted LLM calls
per-component rather than dumping all source into a single prompt.
Each component category gets a specialised prompt with a concrete
template example loaded from project_config.yml, resulting in output
that closely matches the reference documentation format.

The orchestrator is stateless with respect to any particular codebase;
all repo-specific knowledge comes from the YAML config.
"""

import logging
import time
from typing import Dict, List, Optional

from ..config import ConfigLoader
from ..models import FileInfo, ProjectInfo
from ..parsing import CodeParser
from ..llm import LLMFactory, BaseLLMAdapter
from ..llm import prompts as pt
from .context import ContextBuilder

logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """Config-driven orchestrator for multi-file documentation generation.

    Design decision: Rather than a single monolithic LLM call, the
    orchestrator groups parsed files by their classification category and
    issues focused prompts for each group. This yields higher-quality output
    because the LLM receives a smaller, relevant context window and a
    concrete output-format example for each documentation type.
    """

    def __init__(self, config: ConfigLoader):
        """Initialise with a validated configuration.

        Args:
            config: Loaded and validated ConfigLoader instance.
        """
        self.config = config
        self.parser = CodeParser(config.raw)
        self.ctx = ContextBuilder(self.parser)
        self.llm: Optional[BaseLLMAdapter] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def initialise_llm(self) -> None:
        """Create the LLM adapter from configuration."""
        self.llm = LLMFactory.create(self.config)
        logger.info("LLM initialised: %s", self.llm.get_model_name())

    def generate(self, api_key: str) -> Dict[str, str]:
        """Run the full generation pipeline for a single API.

        Args:
            api_key: Key from the ``apis`` section of project_config.yml.

        Returns:
            Dict mapping relative output file paths to their markdown content.
        """
        if not self.llm:
            self.initialise_llm()

        api_cfg = self.config.api_config(api_key)
        display_name = api_cfg["display_name"]
        logger.info("Generating documentation for %s", display_name)

        # 1. Parse source code
        source_paths = self.config.source_paths(api_key)
        dep_paths = self.config.dependent_library_paths(api_key)
        source_projects = self.parser.parse_multiple_projects(source_paths)
        dep_projects = self.parser.parse_multiple_projects(dep_paths)
        all_projects = source_projects + dep_projects

        # Build project_name -> repo-relative source prefix map for correct URLs.
        # e.g., {"Ordering.API": "src/Ordering.API", "Ordering.Domain": "src/Ordering.Domain"}
        self._source_prefix_map: Dict[str, str] = {}
        all_cfg_paths = (
            api_cfg.get("source_paths", []) + api_cfg.get("dependent_libraries", [])
        )
        for proj in all_projects:
            for cfg_path in all_cfg_paths:
                if proj.name in cfg_path:
                    self._source_prefix_map[proj.name] = cfg_path
                    break

        # 2. Classify and group files
        groups = self.ctx.group_by_category(source_projects)

        # 3. Generate content per group
        output_files: Dict[str, str] = {}
        source_prefix = self._source_prefix_for(source_projects)

        for (category, doc_file, doc_title), files in groups.items():
            if not doc_file:
                continue
            logger.info("Generating %s (%d files)", doc_file, len(files))
            content = self._generate_component_doc(
                category, doc_file, doc_title, files, all_projects,
                source_prefix=source_prefix,
            )
            if content:
                api_folder = self.ctx.api_folder_name(source_projects)
                output_files[f"{api_folder}/{doc_file}"] = content

        # Generate feature pages from API endpoint files
        endpoint_files = [
            f for f in self.ctx.all_files(source_projects)
            if f.category == "api_endpoint"
        ]
        if endpoint_files:
            feature_pages = self._generate_feature_docs(
                endpoint_files, all_projects, source_projects
            )
            output_files.update(feature_pages)

        # Generate dependent library docs
        for dep_proj in dep_projects:
            dep_prefix = self._source_prefix_map.get(dep_proj.name, "")
            dep_groups = self.ctx.group_project_files(dep_proj)
            for (cat, dfile, dtitle), files in dep_groups.items():
                if not dfile:
                    continue
                logger.info(
                    "Generating %s/%s (%d files)", dep_proj.name, dfile, len(files)
                )
                content = self._generate_component_doc(
                    cat, dfile, dtitle, files, all_projects,
                    source_prefix=dep_prefix,
                )
                if content:
                    output_files[f"{dep_proj.name}/{dfile}"] = content

        # Generate overview page
        overview = self._generate_overview(display_name, all_projects)
        if overview:
            api_folder = self.ctx.api_folder_name(source_projects)
            overview_name = api_folder.lower().replace(".", "-") + ".md"
            output_files[overview_name] = overview

        # Generate domain index for dependent libraries
        for dep_proj in dep_projects:
            # Collect the doc files that were actually generated for this project.
            prefix = f"{dep_proj.name}/"
            dep_doc_files = [
                key[len(prefix):]
                for key in output_files
                if key.startswith(prefix) and not key.endswith("index.md")
            ]
            index_content = self._generate_domain_index(dep_proj, dep_doc_files)
            if index_content:
                output_files[f"{dep_proj.name}/index.md"] = index_content

        logger.info("Generated %d documentation files", len(output_files))
        return output_files

    # ------------------------------------------------------------------
    # Internal: content generation
    # ------------------------------------------------------------------

    def _source_prefix_for(self, projects: List[ProjectInfo]) -> str:
        """Return the repo-relative source prefix for the first source project."""
        if projects:
            return self._source_prefix_map.get(projects[0].name, "")
        return ""

    def _generate_component_doc(
        self,
        category: str,
        doc_file: str,
        doc_title: str,
        files: List[FileInfo],
        all_projects: List[ProjectInfo],
        source_prefix: str = "",
    ) -> Optional[str]:
        """Generate documentation for a group of files sharing a category."""
        prompt_type = pt.CATEGORY_TO_PROMPT.get(category, "simple_doc")
        template_key = ContextBuilder.template_key_for(prompt_type)
        template_example = self.config.template_example_content(template_key)

        source_code = ContextBuilder.combine_file_content(files)
        class_metadata = self.ctx.build_class_metadata(
            files, project_source_prefix=source_prefix
        )

        prompt_fn = {
            "handler_doc": pt.handler_doc_prompt,
            "query_doc": pt.query_doc_prompt,
            "aggregate_doc": pt.aggregate_doc_prompt,
            "simple_doc": pt.simple_doc_prompt,
            "infrastructure_doc": pt.infrastructure_doc_prompt,
        }.get(prompt_type, pt.simple_doc_prompt)

        prompt = prompt_fn(
            doc_title=doc_title,
            source_code=source_code,
            class_metadata=class_metadata,
            template_example=template_example,
        )

        return self._call_llm(prompt)

    def _generate_feature_docs(
        self,
        endpoint_files: List[FileInfo],
        all_projects: List[ProjectInfo],
        source_projects: List[ProjectInfo],
    ) -> Dict[str, str]:
        """Generate per-feature documentation pages from API endpoint files.

        Design decision: The feature subfolder name is auto-detected from the
        endpoint class name (e.g., OrdersApi -> OrdersApi/) rather than read
        from a hardcoded config value. This ensures each API's features land
        in the correct subfolder without manual config per API.
        """
        results: Dict[str, str] = {}
        template_example = self.config.template_example_content("feature")
        api_folder = self.ctx.api_folder_name(source_projects)
        feature_keywords = self.config.feature_detection.get("feature_keywords", {})

        for fi in endpoint_files:
            # Auto-detect subfolder from endpoint class name (e.g., OrdersApi)
            feature_sub = self._detect_feature_subfolder(fi)

            features = ContextBuilder.detect_features(fi, feature_keywords)
            if not features:
                feature_name = fi.filename.replace(".cs", "")
                handler_info = self.ctx.build_handler_context(fi, all_projects)
                prompt = pt.feature_doc_prompt(
                    feature_name=feature_name,
                    source_code=fi.content,
                    handler_info=handler_info,
                    template_example=template_example,
                )
                content = self._call_llm(prompt)
                if content:
                    path = f"{api_folder}/{feature_sub}/{feature_name}.md"
                    results[path] = content
            else:
                for feature_name in features:
                    handler_info = self.ctx.build_handler_context(fi, all_projects)
                    prompt = pt.feature_doc_prompt(
                        feature_name=feature_name,
                        source_code=fi.content,
                        handler_info=handler_info,
                        template_example=template_example,
                    )
                    content = self._call_llm(prompt)
                    if content:
                        safe_name = feature_name.replace(" ", "")
                        path = f"{api_folder}/{feature_sub}/{safe_name}.md"
                        results[path] = content

        return results

    @staticmethod
    def _detect_feature_subfolder(endpoint_file: FileInfo) -> str:
        """Derive the feature subfolder from the endpoint file's main class name.

        Design decision: Uses the endpoint class name (e.g., 'OrdersApi',
        'CatalogApi') as the subfolder. Falls back to the filename without
        extension if no class is found. This avoids hardcoding per-API config.
        """
        for cls in endpoint_file.classes:
            return cls.name  # e.g., "OrdersApi", "CatalogApi"
        return endpoint_file.filename.replace(".cs", "")

    def _generate_overview(
        self, api_name: str, all_projects: List[ProjectInfo]
    ) -> Optional[str]:
        """Generate the API-level overview page."""
        template_example = self.config.template_example_content("overview")
        component_summary = ContextBuilder.build_component_summary(all_projects)
        source_code = self.parser.get_combined_content(all_projects, max_chars=50_000)

        prompt = pt.overview_doc_prompt(
            api_name=api_name,
            component_summary=component_summary,
            source_code=source_code,
            template_example=template_example,
        )
        return self._call_llm(prompt)

    def _generate_domain_index(
        self,
        project: ProjectInfo,
        generated_doc_files: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Generate an index page for a dependent library.

        Args:
            project: Parsed project metadata.
            generated_doc_files: List of actual doc file basenames generated
                for this project (e.g., ``["Extensions.md", "Repositories.md"]``).
                Used to build correct cross-page links in the index.
        """
        file_list = "\n".join(f"- {fi.relative_path}" for fi in project.files)
        class_list = []
        for fi in project.files:
            for cls in fi.classes:
                class_list.append(f"- {cls.name} ({cls.kind}) in {fi.relative_path}")

        # Build a doc-file-to-classes mapping so the LLM knows where to link.
        doc_links_section = ""
        if generated_doc_files:
            doc_links_section = "\n## Generated Documentation Files (use these for links):\n"
            for doc_file in sorted(generated_doc_files):
                doc_links_section += f"- [{doc_file}](./{doc_file})\n"
            doc_links_section += (
                "\nIMPORTANT: Key Components and Classes links MUST use "
                "relative links like [ClassName](./<DocFile>.md#classname) "
                "pointing to the actual generated files listed above. "
                "Do NOT use same-page anchors.\n"
            )

        doc_tree = f"{project.name}/\n  index.md\n"
        if generated_doc_files:
            for df in sorted(generated_doc_files):
                doc_tree += f"  {df}\n"

        prompt = f"""Generate a brief index/overview page for the {project.name} library.

## Output Structure:

# {project.name} Overview

Brief description of this library's purpose.

## Documentation Structure

```text
{doc_tree}```

## Key Components
(bullet list of main classes — each linked to its documentation page using relative links like [ClassName](./DocFile.md#classname))

## Files
(bullet list of source files)

## Classes
(bullet list of classes — each linked to its documentation page)
{doc_links_section}
## Source Files:
{file_list}

## Classes Found:
{chr(10).join(class_list[:30])}

Generate the index page now. Remember: all links in Key Components and Classes sections must be relative links to the actual generated documentation files listed above, NOT same-page anchors."""
        return self._call_llm(prompt)

    # ------------------------------------------------------------------
    # LLM interaction
    # ------------------------------------------------------------------

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Send a prompt to the LLM with retry logic.

        Returns:
            Generated text, or None on failure after all retries.
        """
        max_attempts = self.config.llm_retry_attempts
        delay = self.config.llm_retry_delay

        for attempt in range(1, max_attempts + 1):
            try:
                response = self.llm.generate(prompt, pt.SYSTEM_PROMPT)
                if response.startswith("```markdown"):
                    response = response[len("```markdown"):].strip()
                if response.startswith("```"):
                    response = response[3:].strip()
                if response.endswith("```"):
                    response = response[:-3].strip()
                return response
            except Exception as exc:
                logger.warning(
                    "LLM call failed (attempt %d/%d): %s",
                    attempt, max_attempts, exc,
                )
                if attempt < max_attempts:
                    time.sleep(delay * attempt)

        logger.error("LLM call failed after %d attempts", max_attempts)
        return None
