# CursorCult Intake (`_intake`)

This repo is the public **intake queue** for adding new projects to the CursorCult GitHub organization.

To add a new rule pack or benchmark to the org, you submit a metadata file via Pull Request.

## How it works (Automation)

The intake process is fully automated via GitHub Actions.

1.  **Submit**: You open a PR adding `submissions/<name>.yml`.
2.  **Validate**: CI checks that the YAML is valid, the name is available, and the source repo exists and is public.
3.  **Approve**: A CursorCult maintainer reviews and merges the PR.
4.  **Create**: Upon merge to `main`, a workflow automatically:
    *   Creates the new repository `CursorCult/<name>` in the organization.
    *   Imports the source code (git history) from your specified `source_url`.
    *   Sets the repository description and website.
    *   Adds "provenance" topics/tags linking back to the intake PR.
    *   Grants you (the submitter) permissions on the new repo (if configured/applicable).

If the automation fails (e.g., name collision after merge), maintainers will resolve it manually.

## Submission Guidelines

### 1. Naming
*   **Rule Packs**: Use PascalCase (e.g., `MyRule`, `NoDeadCode`). Do not use prefixes.
*   **Benchmarks**: Must be named `_benchmark_<RULE>` (e.g., `_benchmark_TDD`).

### 2. Format
Copy `submissions/_template.yml` to `submissions/<your-project>.yml`.

```yaml
name: MyRule
description: "A short, clear description of what this rule enforces."
source_url: "https://github.com/username/my-rule-repo.git"
maintainer: "username"
```

### 3. Source Repository
Your source repository must contain a valid `RULE.md` (for rules) or benchmark structure (for benchmarks) at the root.

## Links

- Cursor (the editor): https://cursor.com
- Cursor rule file format (`RULE.md`): https://cursor.com/docs/context/rules#rulemd-file-format
- Benchmark Results: https://github.com/CursorCult/_results
- Standard Metrics: https://github.com/CursorCult/_metrics
- **Search Registry**: https://cursorcult.github.io/_intake/