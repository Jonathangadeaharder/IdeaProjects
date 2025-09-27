{
  "name": "workflow-pattern",
  "description": "Standard workflow pattern for development tasks",
  "steps": [
    {
      "step": 1,
      "type": "analyze",
      "description": "Analyze first using appropriate slash commands",
      "commands": [
        "/codereview",
        "/patterns",
        "/testing",
        "/security",
        "/parallel",
        "/architecture",
        "/comments",
        "/documentation"
      ]
    },
    {
      "step": 2,
      "type": "plan",
      "description": "Create improvement plan with specific actionable tasks"
    },
    {
      "step": 3,
      "type": "review",
      "description": "User reviews and customizes the plan"
    },
    {
      "step": 4,
      "type": "execute",
      "description": "Execute plan making actual code changes"
    },
    {
      "step": 5,
      "type": "document",
      "description": "Document completion and any problems encountered"
    }
  ],
  "requirements": [
    "Analyze first using appropriate slash commands",
    "Create improvement plan with specific actionable tasks",
    "User reviews and customizes the plan",
    "Execute plan making actual code changes",
    "Document completion and any problems encountered",
    "For large changes, propose a short stepwise plan; update as you progress",
    "Validate with targeted pytest runs in the venv; then broader suite"
  ]
}
