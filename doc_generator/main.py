"""
Main Entry Point

Run the documentation generator from command line:
    python -m doc_generator.main                    # Uses default (ordering)
    python -m doc_generator.main --api catalog      # Document Catalog API
    python -m doc_generator.main --api basket       # Document Basket API
    python -m doc_generator.main --list             # List available APIs
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from doc_generator.config_loader import ConfigLoader
from doc_generator.doc_generator import DocumentationGenerator


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Automated Documentation Generator for .NET APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m doc_generator.main                    # Document Ordering API (default)
  python -m doc_generator.main --api catalog      # Document Catalog API
  python -m doc_generator.main --api basket       # Document Basket API
  python -m doc_generator.main --list             # List available APIs
  python -m doc_generator.main --api custom       # Document custom API (set paths in config.env)
        """
    )
    
    parser.add_argument(
        "--api", "-a",
        type=str,
        default=None,
        help="API to document: ordering, catalog, basket, or custom"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available APIs and exit"
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show what would be documented without calling LLM"
    )
    
    return parser.parse_args()


def list_available_apis():
    """List all available APIs that can be documented."""
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║               AVAILABLE APIs TO DOCUMENT                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    apis = ConfigLoader.get_available_apis()
    configs = ConfigLoader.API_CONFIGS
    
    print("  API Name        Source Paths")
    print("  " + "─" * 55)
    
    for api in apis:
        if api in configs:
            paths = configs[api]["paths"]
            print(f"  {api:<15} {paths}")
        else:
            print(f"  {api:<15} (configure in config.env)")
    
    print()
    print("Usage:")
    print("  python -m doc_generator.main --api <api_name>")
    print()


def main():
    """Main entry point for the documentation generator."""
    args = parse_arguments()
    
    # Handle --list flag
    if args.list:
        list_available_apis()
        return 0
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       AUTOMATED DOCUMENTATION GENERATOR                     ║")
    print("║       Generating documentation for .NET APIs                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    try:
        # Load configuration with optional API override
        print("Loading configuration...")
        config = ConfigLoader(target_api=args.api)
        
        # Show target API
        print(f"  Target API: {config.api_name}")
        print(f"  Output File: {config.output_filename}")
        
        # Validate configuration
        print("Validating configuration...")
        config.validate()
        print(f"  LLM Provider: {config.llm_provider}")
        print(f"  Source Paths: {[p.name for p in config.source_paths]}")
        print(f"  Include Diagrams: {config.include_diagrams}")
        print()
        
        # Dry run mode
        if args.dry_run:
            print("DRY RUN MODE - Not calling LLM")
            print()
            print("Would document the following projects:")
            for path in config.source_paths:
                print(f"  - {path}")
            print()
            print(f"Output would be saved to: {config.output_dir / config.output_filename}")
            return 0
        
        # Create generator
        generator = DocumentationGenerator(config)
        
        # Run generation
        output_path = generator.run()
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nTo fix this:")
        print("  1. Copy config.env.template to .env (or config.env)")
        print("     cp config.env.template .env")
        print("  2. Add your API key to .env")
        print("  3. Run: make generate")
        return 1
        
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        return 1
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
