# ============================================================
# Automated Documentation Generator - Makefile
# ============================================================
# All commands use project_config.yml for settings.
# API keys are loaded from .env
# ============================================================

PYTHON    := python3
VENV      := venv
ACTIVATE  := source $(VENV)/bin/activate
MODULE    := doc_generator

# Read mkdocs config path from project_config.yml (fallback to src/docs)
MKDOCS_DIR := src/docs

# ============================================================
# Setup
# ============================================================

.PHONY: setup
setup: ## Create virtual environment and install dependencies
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -r requirements.txt
	@echo ""
	@echo "Setup complete. Next steps:"
	@echo "  1. cp project_config.yml.template project_config.yml"
	@echo "  2. cp .env.template .env"
	@echo "  3. Edit both files with your settings"
	@echo "  4. make generate API=ordering"

# ============================================================
# Generation
# ============================================================

.PHONY: generate
generate: ## Generate docs for a single API (usage: make generate API=ordering)
ifndef API
	@echo "Usage: make generate API=<api_key>"
	@echo "Run 'make list' to see available APIs"
	@exit 1
endif
	$(ACTIVATE) && $(PYTHON) -m $(MODULE) --api $(API)

.PHONY: regenerate
regenerate: ## Clean + regenerate docs for an API (usage: make regenerate API=ordering)
ifndef API
	@echo "Usage: make regenerate API=<api_key>"
	@exit 1
endif
	$(ACTIVATE) && $(PYTHON) -m $(MODULE) --api $(API) --clean

.PHONY: generate-all
generate-all: ## Generate docs for ALL APIs in project_config.yml
	$(ACTIVATE) && \
	APIS=$$($(PYTHON) -c "import yaml; print(' '.join(yaml.safe_load(open('project_config.yml')).get('apis',{}).keys()))") && \
	echo "Generating for: $$APIS" && \
	for api in $$APIS; do \
		echo ""; echo "--- Generating: $$api ---"; \
		$(PYTHON) -m $(MODULE) --api $$api || exit 1; \
	done

.PHONY: list
list: ## List available APIs from project_config.yml
	$(ACTIVATE) && $(PYTHON) -m $(MODULE) --list

.PHONY: dry-run
dry-run: ## Parse and classify files without LLM calls (usage: make dry-run API=ordering)
ifndef API
	@echo "Usage: make dry-run API=<api_key>"
	@exit 1
endif
	$(ACTIVATE) && $(PYTHON) -m $(MODULE) --api $(API) --dry-run

# ============================================================
# MkDocs Server
# ============================================================

.PHONY: serve
serve: ## Start MkDocs dev server
	$(ACTIVATE) && cd $(MKDOCS_DIR) && mkdocs serve

.PHONY: build
build: ## Build static MkDocs site
	$(ACTIVATE) && cd $(MKDOCS_DIR) && mkdocs build

.PHONY: kill
kill: ## Kill any running MkDocs server
	@pkill -f "mkdocs serve" 2>/dev/null && echo "MkDocs server stopped" || echo "No MkDocs server running"

# ============================================================
# Validation
# ============================================================

.PHONY: validate-config
validate-config: ## Validate project_config.yml
	$(ACTIVATE) && $(PYTHON) -c "\
		from doc_generator.config import ConfigLoader; \
		c = ConfigLoader(); \
		print('Config valid. APIs:', list(c.apis.keys())); \
		print('LLM:', c.llm_provider, c.llm_model)"

# ============================================================
# Utilities
# ============================================================

.PHONY: clean
clean: ## Remove generated documentation files (dry-run)
	@echo "Cleaning generated docs (dry-run)..."
	@$(ACTIVATE) && $(PYTHON) -m doc_generator.output.clean --dry-run
	@echo "Run 'make clean-confirm' to actually delete"

.PHONY: clean-confirm
clean-confirm: ## Actually remove generated docs (destructive)
	@$(ACTIVATE) && $(PYTHON) -m doc_generator.output.clean

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
