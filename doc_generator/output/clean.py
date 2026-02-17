"""Clean generated documentation files.

Reads API configuration from project_config.yml and removes the
corresponding generated directories and overview files from the docs output.
"""

import shutil
import sys
from pathlib import Path

import yaml


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    config_path = Path("project_config.yml")
    if not config_path.exists():
        print("Error: project_config.yml not found")
        sys.exit(1)

    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    docs_dir = Path(cfg.get("output", {}).get("docs_dir", "docs"))
    apis = cfg.get("apis", {})

    targets: list[Path] = []
    for key, api in apis.items():
        all_paths = api.get("source_paths", []) + api.get("dependent_libraries", [])
        for sp in all_paths:
            name = sp.rstrip("/").split("/")[-1]
            d = docs_dir / name
            if d.exists():
                targets.append(d)
        overview = docs_dir / f"{key}-api.md"
        if overview.exists():
            targets.append(overview)

    unique = sorted(set(targets), key=str)

    if not unique:
        print("Nothing to clean.")
        return

    if dry_run:
        print("Would remove:")
        for t in unique:
            print(f"  {t}")
    else:
        for t in unique:
            if t.is_dir():
                shutil.rmtree(t)
            else:
                t.unlink()
            print(f"  Removed: {t}")
        print(f"Cleaned {len(unique)} items.")


if __name__ == "__main__":
    main()
