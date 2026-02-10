"""CLI entry point for the documentation generator.

Design decision: The CLI is intentionally minimal -- it accepts an API key
(from project_config.yml ``apis`` section) and optional flags. All
behaviour is driven by the YAML config, so the CLI does not need numerous
arguments.
"""

import argparse
import logging
import sys
from pathlib import Path

from .config import ConfigLoader
from .generation import DocumentationGenerator
from .output import DocumentAssembler


def _setup_logging(level_name: str) -> None:
    """Configure root logging with a consistent format."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Automated Documentation Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Configuration is loaded from project_config.yml and .env",
    )
    parser.add_argument(
        "--api",
        type=str,
        help="API key to generate docs for (must exist in project_config.yml apis section)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_apis",
        help="List available APIs from project_config.yml and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and classify files without calling the LLM",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove previously generated files for the target API before writing",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to project_config.yml (default: auto-detect in project root)",
    )
    return parser.parse_args()


def main() -> None:
    """Run the documentation generation pipeline."""
    args = parse_arguments()

    # Load configuration.
    config_path = Path(args.config) if args.config else None
    config = ConfigLoader(config_path=config_path)
    _setup_logging(config.log_level)

    logger = logging.getLogger(__name__)
    logger.info("Documentation Generator v2.0")

    # List mode.
    if args.list_apis:
        print("\nAvailable APIs (from project_config.yml):\n")
        for key, api_cfg in config.apis.items():
            name = api_cfg.get("display_name", key)
            paths = ", ".join(api_cfg.get("source_paths", []))
            deps = ", ".join(api_cfg.get("dependent_libraries", [])) or "(none)"
            print(f"  {key:20s} {name}")
            print(f"  {'':20s} Sources: {paths}")
            print(f"  {'':20s} Dependencies: {deps}")
            print()
        return

    # Determine which API to generate.
    api_key = args.api
    if not api_key:
        available = list(config.apis.keys())
        if len(available) == 1:
            api_key = available[0]
            logger.info("Auto-selected API: %s", api_key)
        else:
            print(f"Please specify --api. Available: {', '.join(available)}")
            sys.exit(1)

    # Validate the API key early to avoid tracebacks downstream.
    if api_key not in config.apis:
        available = ", ".join(config.apis.keys())
        print(f"Error: API '{api_key}' not found in project_config.yml.")
        print(f"Available APIs: {available}")
        print("Run with --list for details.")
        sys.exit(1)

    # Dry-run mode: parse and classify only.
    if args.dry_run:
        logger.info("Dry-run mode: parsing and classifying only")
        from .parsing import CodeParser

        parser = CodeParser(config.raw)
        all_paths = config.source_paths(api_key) + config.dependent_library_paths(api_key)
        projects = parser.parse_multiple_projects(all_paths)

        for proj in projects:
            print(f"\n{proj.name} ({proj.total_files} files):")
            for fi in proj.files:
                cls_names = [c.name for c in fi.classes]
                print(f"  [{fi.category:25s}] {fi.relative_path}  classes={cls_names}")
        return

    # Full generation.
    print("=" * 60)
    print("AUTOMATED DOCUMENTATION GENERATOR v2.0")
    print("=" * 60)

    generator = DocumentationGenerator(config)
    generated = generator.generate(api_key)

    if not generated:
        logger.error("No documentation was generated")
        sys.exit(1)

    # Assemble output.
    assembler = DocumentAssembler(config)
    if args.clean:
        assembler.clean_api_output(api_key, generated)
    written = assembler.assemble(generated)

    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nFiles written: {len(written)}")
    print(f"Output directory: {config.output_docs_dir}")
    print(f"\nTo view in browser:")
    print(f"  cd {config.mkdocs_config_path.parent}")
    print(f"  mkdocs serve")
    print(f"  Open http://127.0.0.1:8000")


if __name__ == "__main__":
    main()
