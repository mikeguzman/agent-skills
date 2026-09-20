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

The repo is public, so no token is involved.

## Las preguntas abiertas, en una sola lista

```
./tools/preguntas-abiertas.py labsanmartincr/lsm-ai-agents
./tools/preguntas-abiertas.py <owner/repo> --para Leo
./tools/preguntas-abiertas.py <owner/repo> --porque
```

Lee los issues con etiqueta `req:*` y agrupa sus preguntas **por quién las
contesta**, no por issue. Con un pedido a la vez no hace falta; con cuatro,
sí — el 2026-09-19, con tres vivos, la pregunta que hubo que hacer fue
«pasame las preguntas que faltan, se me enredó todo».

Funciona porque la skill exige un formato fijo para cada pregunta (ver el
paso 6). También lee el formato viejo, sin negritas, para no perder issues
analizados antes.

Con `--repo-local` y `--plan` también avisa cuando la bandera
`req:esperando` y el plan dejaron de coincidir — la bandera no se quita
sola, se levanta cuando alguien mueve la tarea de `Esperando` a `Ahora`, y
nada vigila eso. Los planes se leen de la **rama por defecto**, no del árbol
de trabajo: un checkout parado en otra rama produce desfases inventados, y
eso pasó de verdad el 2026-09-19.

## El próximo número de fase

```
./tools/siguiente-fase.py ~/Projects/x --repo owner/repo
```

El más alto en uso más uno, mirando planes, diarios **y PR abiertos**. Ese
tercero es el que importa: un traspaso sin mergear es invisible en los dos
primeros, y así es como dos pedidos piden el mismo número. Pasó el
2026-09-19 y salió bien de casualidad.

La skill se lo calcula sola (paso 2 del traspaso); esto es para verificar
sin depender del agente.

## Use in CI

Copy `templates/requirements-analysis.yml` into a repo's
`.github/workflows/`. It runs `anthropics/claude-code-action` with:

```yaml
plugin_marketplaces: "https://github.com/mikeguzman/agent-skills.git"
plugins: "product-owner@mikes-skills"
```

**This repo is public on purpose.** A workflow runs with its own org's
GitHub App token, which cannot read a private repo under a different
owner — measured on 2026-09-19, the runner failed with *"Failed to clone
marketplace repository"*. A private marketplace would need a cross-owner
token per organization; public needs none and works from every one.

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
