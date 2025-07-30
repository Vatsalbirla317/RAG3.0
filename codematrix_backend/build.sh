#!/usr/bin/env bash
# exit on error
set -o errexit

# Step 1: Install all Python packages from requirements.txt
pip install -r requirements.txt

# Step 2: Install the tree-sitter language parsers required by LangChain
python -c "from langchain_community.document_loaders.parsers.language.tree_sitter_parser import LanguageParser; LanguageParser.install_grammars()" 