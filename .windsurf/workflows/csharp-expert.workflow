{
  "name": "csharp-expert",
  "description": "C# language expert for specialized C# development tasks",
  "steps": [
    {
      "type": "specialist",
      "language": "csharp",
      "description": "Invoke proactively when working with C# technologies"
    },
    {
      "type": "apply",
      "description": "Leverage specialized knowledge for C#-specific best practices"
    }
  ],
  "triggers": [
    "csharp-expert"
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
    "naming": "PascalCase classes/methods, camelCase fields/variables",
    "async": "Always use async/await, suffix methods with 'Async'",
    "nulls": "Use nullable reference types (?), null-coalescing (??, ?.)",
    "resources": "Use using statements for disposables",
    "collections": "Prefer interfaces (IEnumerable, IList) in APIs"
  }
}
