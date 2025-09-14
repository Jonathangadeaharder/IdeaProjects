#!/bin/bash
# Script to run code quality checks

echo "Running Ruff linter..."
ruff check .

echo "Running Ruff formatter..."
ruff format .

echo "Running tests..."
pytest

echo "All checks completed!"