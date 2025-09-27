{
  "name": "security",
  "description": "Security analysis and create improvement plan",
  "steps": [
    {
      "type": "analyze",
      "analysis_type": "security",
      "description": "Security analysis and create improvement plan"
    },
    {
      "type": "plan",
      "description": "Create specific actionable tasks for security improvements"
    }
  ],
  "triggers": [
    "/security"
  ],
  "requirements": [
    "Always use analysis commands before making changes",
    "Create improvement plan with specific actionable tasks",
    "User reviews and customizes the plan",
    "Execute plan making actual code changes",
    "Document completion and any problems encountered"
  ]
}
