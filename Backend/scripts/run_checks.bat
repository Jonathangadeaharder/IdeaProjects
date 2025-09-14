@echo off
REM Script to run code quality checks on Windows

echo Running Ruff linter...
ruff check .

echo Running Ruff formatter...
ruff format .

echo Running tests...
pytest

echo All checks completed!