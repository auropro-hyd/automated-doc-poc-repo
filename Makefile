# ============================================
# AUTOMATED DOCUMENTATION GENERATOR
# Makefile for easy command execution
# ============================================

# Default Python command (override with: make PYTHON=python3.11 ...)
PYTHON = python3

# Virtual environment directory
VENV = venv

# Default API to document
API = ordering

# ============================================
# SETUP COMMANDS
# ============================================

.PHONY: setup
setup: venv install ## Complete setup (create venv + install dependencies)
	@echo "✅ Setup complete!"
	@echo "Next steps:"
	@echo "  1. Copy .env.template to .env (or config.env)"
	@echo "  2. Add your API key to .env"
	@echo "  3. Run: make generate"

.PHONY: venv
venv: ## Create virtual environment
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "✅ Virtual environment created"
	@echo "Activate with: source $(VENV)/bin/activate"

.PHONY: install
install: ## Install Python dependencies
	@echo "Installing dependencies..."
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# ============================================
# DOCUMENTATION GENERATION
# ============================================

.PHONY: generate
generate: ## Generate documentation for default API (ordering)
	@echo "Generating documentation for $(API) API..."
	$(VENV)/bin/python -m doc_generator.main --api $(API)

.PHONY: generate-ordering
generate-ordering: ## Generate documentation for Ordering API
	$(VENV)/bin/python -m doc_generator.main --api ordering

.PHONY: generate-catalog
generate-catalog: ## Generate documentation for Catalog API
	$(VENV)/bin/python -m doc_generator.main --api catalog

.PHONY: generate-basket
generate-basket: ## Generate documentation for Basket API
	$(VENV)/bin/python -m doc_generator.main --api basket

.PHONY: generate-all
generate-all: ## Generate documentation for ALL APIs
	@echo "Generating documentation for all APIs..."
	$(VENV)/bin/python -m doc_generator.main --api ordering
	$(VENV)/bin/python -m doc_generator.main --api catalog
	$(VENV)/bin/python -m doc_generator.main --api basket
	@echo "✅ All documentation generated!"

.PHONY: dry-run
dry-run: ## Dry run (show what would be generated without calling LLM)
	$(VENV)/bin/python -m doc_generator.main --api $(API) --dry-run

# ============================================
# DOCUMENTATION VIEWING
# ============================================

.PHONY: serve
serve: ## Start MkDocs server (view docs at http://127.0.0.1:8000)
	@echo "Starting documentation server..."
	@echo "Open http://127.0.0.1:8000 in your browser"
	$(VENV)/bin/mkdocs serve

.PHONY: build
build: ## Build static documentation site
	$(VENV)/bin/mkdocs build
	@echo "✅ Documentation built in 'site/' folder"

# ============================================
# SERVER MANAGEMENT
# ============================================

.PHONY: kill
kill: ## Kill MkDocs server running on port 8000
	@echo "Killing any process on port 8000..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No process found on port 8000"
	@echo "✅ Port 8000 is now free"

.PHONY: restart
restart: kill serve ## Restart MkDocs server (kill + serve)

# ============================================
# UTILITY COMMANDS
# ============================================

.PHONY: list
list: ## List available APIs to document
	$(VENV)/bin/python -m doc_generator.main --list

.PHONY: clean
clean: ## Clean generated files (keeps venv)
	@echo "Cleaning generated files..."
	rm -rf local_dev/generated_docs/*.md
	rm -rf site/
	@echo "✅ Cleaned"

.PHONY: clean-all
clean-all: clean ## Clean everything including virtual environment
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "✅ All cleaned"

.PHONY: test
test: ## Run basic tests
	@echo "Running tests..."
	$(VENV)/bin/python -c "from doc_generator.code_parser import CodeParser; print('✅ Code parser OK')"
	$(VENV)/bin/python -c "from doc_generator.config_loader import ConfigLoader; print('✅ Config loader OK')"
	$(VENV)/bin/python -c "from doc_generator.llm_adapter import LLMFactory; print('✅ LLM adapter OK')"
	@echo "✅ All tests passed!"

# ============================================
# HELP
# ============================================

.PHONY: help
help: ## Show this help message
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║       AUTOMATED DOCUMENTATION GENERATOR                     ║"
	@echo "║       Available Make Commands                               ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make setup                    # First-time setup"
	@echo "  make generate                 # Generate docs for ordering API"
	@echo "  make generate API=catalog     # Generate docs for catalog API"
	@echo "  make generate-all             # Generate docs for all APIs"
	@echo "  make serve                    # View documentation in browser"
	@echo ""

# Default target
.DEFAULT_GOAL := help
