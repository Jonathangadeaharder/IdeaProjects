# Review Checklists

Use these checklists for every pull request. Authors must confirm each item prior to requesting
review; reviewers should verify the same points.

## Author Pre-PR Checklist
- [ ] Contract updates are documented, versioned, and approved by stakeholders.
- [ ] All generated artifacts (OpenAPI client, schema stubs) are regenerated and committed.
- [ ] Protective tests exist for happy path, invalid input, and boundary scenarios.
- [ ] Tests run green locally (`pytest`, `npm run test`, contract suites, linting).
- [ ] Documentation (`docs/`, feature READMEs) reflects the new or changed behavior.
- [ ] Rollback or migration plan is described for breaking contract changes.

## Reviewer Contract Checklist
- [ ] Contract changes align with `CONTRACTDRIVENDEVELOPMENT.MD` principles.
- [ ] Version increments follow semantic rules and communicate breaking changes.
- [ ] Consumer impact is documented with migration steps or temporary shims.
- [ ] Automated contract tests cover the updated endpoints or schemas.
- [ ] Mock/stub usage is justified and derives from generated contract artifacts.

## Reviewer Testing Checklist
- [ ] Tests are behavior-focused and avoid internal implementation assertions.
- [ ] Happy path, invalid input, and single high-value boundary tests are present (unless the author
      justifies a different mix).
- [ ] Test names and docstrings clearly describe the behavior under test.
- [ ] Shared fixtures/utilities are used instead of ad-hoc setup.
- [ ] Coverage includes affected services and integration points.
- [ ] Failure messages or logging include enough context to debug contract violations.

## Reviewer Documentation and Tooling Checklist
- [ ] Tooling instructions (scripts, commands) for contract/schema updates are accurate.
- [ ] CONTRIBUTING, README, or service docs reference the new workflows when necessary.
- [ ] CI configuration (if touched) enforces contract and protective testing rules.
- [ ] Manual steps for testing or deploying are callouts in the PR description.
