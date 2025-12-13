# CursorCult Intake (`_intake`)

This repo is the public **intake queue** for adding new projects to the CursorCult GitHub organization.

GitHub does **not** allow a pull request whose payload is “a repository.” A PR can only contain **git objects inside an existing repository**.

However, there are **two correct patterns** that achieve the same outcome.

## Pattern 1 — Repository-as-PR (canonical)

A repository is submitted by mirroring its contents into a PR against a central repo.

- Contributor creates their own repo, then opens a PR that adds it under `projects/<project-name>/`.
- After merge, automation creates `CursorCult/<project-name>` and imports contents (optionally preserving history).

This is how many large ecosystems handle open intake, but it can create monorepo/registry bloat.

## Pattern 2 — Metadata PR (recommended here)

The PR contains **no code**, only a declaration (a single YAML file).

Example shape:

```yaml
project:
  repo: cursorcult-foo
  source: https://github.com/user/foo
  owner: user
  license: MIT
  description: One-line summary
```

On merge, automation can:

- validate metadata
- create `CursorCult/<repo>`
- import the source repo
- assign permissions
- tag provenance

## Benchmark repos

If you’re proposing a benchmark for a rule, use the naming convention:

- `_benchmark_<RULE>`

Benchmarks should reuse standard metrics from:

- https://github.com/CursorCult/_metrics

Benchmarks should publish results by PR into:

- https://github.com/CursorCult/_results
  - `rules/<RULE>/<language>/RESULTS.md`

## What is not possible

- PR that creates a repo directly
- PR against the org itself
- PR that spans multiple repos

GitHub’s unit of change is **one repo at a time**.

## Submit a project

1. Fork this repo.
2. Copy `submissions/_template.yml` to `submissions/<your-project>.yml` and fill it in.
3. Open a PR.

## Links

- Cursor (the editor): https://cursor.com
- Cursor rule file format (`RULE.md`): https://cursor.com/docs/context/rules#rulemd-file-format
