{
  "name": "cpp-expert",
  "description": "C++ language expert for specialized C++ development tasks",
  "steps": [
    {
      "type": "specialist",
      "language": "cpp",
      "description": "Invoke proactively when working with C++ technologies"
    },
    {
      "type": "apply",
      "description": "Leverage specialized knowledge for C++-specific best practices"
    }
  ],
  "triggers": [
    "cpp-expert"
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
    "naming": "snake_case variables/functions, PascalCase classes",
    "memory": "Smart pointers (unique_ptr, shared_ptr), avoid raw pointers",
    "const": "Const correctness throughout",
    "raii": "Resource management via constructors/destructors",
    "stl": "Prefer STL algorithms over manual loops"
  }
}
