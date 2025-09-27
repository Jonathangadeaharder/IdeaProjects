{
  "name": "enhanced-testing-workflow",
  "description": "Enhanced testing workflow for creating test suites",
  "steps": [
    {
      "step": 1,
      "type": "analyze",
      "description": "Analyze first using /testing command when creating test suites",
      "command": "/testing"
    },
    {
      "step": 2,
      "type": "validate",
      "description": "Apply pre-flight checks for every individual test before writing",
      "checks": [
        "Does this test verify observable behavior, not implementation?",
        "Will this test survive refactoring without changes?",
        "Does this test fail meaningfully when the feature breaks?",
        "Am I testing the public contract, not internal mechanisms?",
        "Are there any hard-coded paths, credentials, or external dependencies?",
        "Am I using semantic selectors instead of array indices?"
      ]
    },
    {
      "step": 3,
      "type": "create",
      "description": "Create behavior-focused tests that verify public contracts"
    },
    {
      "step": 4,
      "type": "review",
      "description": "Review and validate tests against quality guidelines"
    },
    {
      "step": 5,
      "type": "document",
      "description": "Document any anti-patterns avoided in commit messages"
    }
  ],
  "requirements": [
    "Analyze first using /testing command when creating test suites",
    "Apply pre-flight checks for every individual test before writing",
    "Create behavior-focused tests that verify public contracts",
    "Review and validate tests against quality guidelines",
    "Document any anti-patterns avoided in commit messages",
    "Never create tests that count mock method calls instead of checking outcomes",
    "Never create tests that accept multiple status codes as valid",
    "Never create tests that test language features instead of business logic",
    "Never create tests that use brittle selectors (array indices, exact CSS values)",
    "Never create tests that pass with assert True or similar meaningless assertions",
    "Never create tests that silence failing behaviour via skip, xfail, fixme, pending",
    "Never create tests that hard-code absolute file paths or Windows-specific paths",
    "Never create tests that print results instead of asserting expected outcomes",
    "Never create tests that expose credentials, tokens, or sensitive data",
    "Never create tests that depend on external servers or real file systems without isolation"
  ]
}
