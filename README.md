# agent-skills

A Claude Code plugin marketplace with the skills I reuse across projects.
Each plugin is a method, not project knowledge: it reads the repo it runs
in (`AGENTS.md`, plans, that repo's own skills) and applies the method
there. Project-specific rules stay in each project.

## Plugins

| Plugin | What it does |
| --- | --- |
| `product-owner` | Analyzes a requirement that arrived as a GitHub issue — usually from a voice note — against the repo's plans, code and rules, writes the analysis into the issue, and hands an approved issue into the repo's plan. |

## Install locally

```
/plugin marketplace add mikeguzman/agent-skills
/plugin install product-owner@mikes-skills
```

Private repo: your `gh`/git credentials are used automatically.

## Use in CI

Copy `templates/requirements-analysis.yml` into a repo's
`.github/workflows/`. It runs `anthropics/claude-code-action` with:

```yaml
plugin_marketplaces: "https://github.com/mikeguzman/agent-skills.git"
plugins: "product-owner@mikes-skills"
```

Because this repo is private and lives under a different owner than the
repos that use it, the job needs read access to it: either make this repo
public (it holds no secrets) or pass a `github_token` with read access —
decide on the first real run.

## Where this fits

The full flow — voice note → Mike's Brain → GitHub issue and Project →
this skill in Actions → the maintainer's decision → the repo's plan — is
documented in the "Del Voicenote al Plan" design (2026-09-19). This repo
is the *method* layer of that design; the intake lives in
`mikes-brain-mcp`, the runtime workflow and the plan handoff live in each
target repo.

## Naming

The marketplace is called **`mikes-skills`**, not `agent-skills` like the
repo: Claude Code reserves names matching official Anthropic marketplaces
and rejects them with *"The name 'agent-skills' is reserved for official
Anthropic marketplaces"*. Repo name and marketplace name are independent —
callers use the `name` field in `.claude-plugin/marketplace.json`.

## Writing a skill here

- `plugins/<name>/.claude-plugin/plugin.json` and
  `plugins/<name>/skills/<name>/SKILL.md`; register it in
  `.claude-plugin/marketplace.json`.
- Frontmatter `description` says *when* to use it, in the words a person
  would use — that is what triggers it.
- No project names inside the method. If a step depends on the project,
  the skill says "read the repo's AGENTS.md for X", not what X is.
