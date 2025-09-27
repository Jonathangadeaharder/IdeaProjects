{
  "name": "codereview",
  "description": "Analyze code quality and create improvement plan",
  "steps": [
    {
      "type": "analyze",
      "analysis_type": "code_quality",
      "description": "Analyze code quality and create improvement plan"
    },
    {
      "type": "plan",
      "description": "Create specific actionable tasks for code quality improvements"
    }
  ],
  "triggers": [
    "/codereview"
  ],
  "requirements": [
    "Always use analysis commands before making changes",
    "Create improvement plan with specific actionable tasks",
    "User reviews and customizes the plan",
    "Execute plan making actual code changes",
    "Document completion and any problems encountered"
  ]
}
