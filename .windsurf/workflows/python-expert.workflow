{
  "name": "python-expert",
  "description": "Python language expert for specialized Python development tasks",
  "steps": [
    {
      "type": "specialist",
      "language": "python",
      "description": "Invoke proactively when working with Python technologies"
    },
    {
      "type": "apply",
      "description": "Leverage specialized knowledge for Python-specific best practices"
    }
  ],
  "triggers": [
    "python-expert"
  ],
  "requirements": [
    "Language experts are available: python-expert, cpp-expert, csharp-expert, react-expert, plantuml-expert, latex-expert",
    "Invoke proactively when working with specific technologies",
    "Leverage specialized knowledge for language-specific best practices",
    "Keep changes minimal and focused; do not refactor unrelated code",
    "Follow existing naming and structure; no one-letter variables",
    "Avoid inline comments unless necessary for clarity"
  ],
  "standards": {
    "naming": "snake_case everything except classes (PascalCase)",
    "types": "Use type hints for parameters and returns",
    "idioms": "List comprehensions, context managers, enumerate()",
    "docs": "Docstrings for all public functions/classes",
    "strings": "Prefer f-strings over .format() or % formatting"
  }
}
