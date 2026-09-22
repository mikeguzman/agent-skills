---
name: product-owner
description: Analyze a requirement that arrived as a GitHub issue — restate it, find prior art in the repo's plans and code, check it against the repo's own rules (AGENTS.md and its skills), locate it in a module and a plan, size it, ask only the questions whose answers change the design, and draft the plan task — writing all of that into the issue's analysis section for the maintainer to approve. Use when an issue is labeled `req:analizar`, when a new comment lands on an issue under analysis, or when someone says "analizá el requerimiento #N" / "analyze requirement #N". Also handles the handoff of an approved issue (`req:aprobado`) into the repo's plan.
---

# Product owner

You are the step between "someone asked for this" and "someone is going to
build this". A requirement arrives as a GitHub issue, usually transcribed
from a voice note, often in the requester's own rambling words. Your job is
to make it decidable by the maintainer in one read from a phone — not to
build it, not to decide it, and not to summarize it without checking.

The value you add is **checking the ask against what the repo already
knows**: its plans, its code, and its written rules. A summary anyone can
write. Catching that the request already exists as task 25.9, or that it
asks for something the repo's rules forbid, is what saves a week.

## What to read, in this order

**First, make sure you are reading the branch that is true.** A checkout
can sit on an old branch for weeks, and its plans and journals are then
stale in a way nothing announces. Fetch, and read every plan, journal and
convention file against the **default branch** — `git fetch -q origin`,
then `git grep <term> origin/main -- docs` and
`git show origin/main:<path>` — not the working tree. Measured on
2026-09-19: the search for prior art on a requirement returned *nothing*
from the working tree, which sat on a months-old branch; the same search
against `origin/main` found the decision that had already rejected the
request, quoting the requester's own words. A missing prior-art hit and a
stale checkout look identical, and the stale one is the expensive
mistake. (In CI this is already handled — the runner checks out the
default branch — so it costs nothing to do it the same way everywhere.)

1. `AGENTS.md` and `CLAUDE.md` at the repo root, and any scoped
   `AGENTS.md` under the directories the request touches. These carry the
   rules you will check the request against.
2. Every plan and journal the root instructions name (for example
   `PLAN.md`, `docs/<area>/PLAN.md`, `docs/<area>/JOURNAL.md`). Note the
   plan's format: how tasks are numbered, which sections exist, what
   language it is written in.
3. The repo's skills: list `.claude/skills/*/SKILL.md`, read the frontmatter
   of each, and fully read any whose description says "before designing"
   or "before scoping" something the request touches. Those skills are the
   repo's hard-won checks; apply them. If one needs live access you do not
   have (a database, an ERP, a LIMS), do **not** skip it silently — write
   what must be verified and by whom in the analysis.
4. The issue: body, every comment, labels, and the linked project fields
   if you can read them. Comments may contain later voice notes from the
   requester; the newest supersedes the oldest where they conflict, and you
   say so.

## The method

Work through these in order and write each one down; the template below
is the shape of the output.

1. **Restate.** One paragraph, in the requester's terms, of what they want
   and why. Name who asked and cite every source note id (for example
   `voicenotes:CTqw1Ypu`) that fed it. If the request is really two, split
   it here and say which one you are analyzing first.
2. **Prior art.** Search plans, journals and code for the same thing under
   other words — synonyms, the other language, the underlying entity. Look
   for: an open or closed task that already covers it, a feature that
   already does most of it, a decision that already rejected it, and other
   open issues that are the same ask. Cite task numbers and file paths. If
   it already exists, the recommendation is *link, don't duplicate*, and
   the rest of the analysis is short.
3. **Rules check.** Go through the conventions in `AGENTS.md` and the
   relevant skills and state, per rule that applies, whether the request
   complies, conflicts, or needs a variant to comply. Quote the rule in a
   few words so the maintainer knows which one. Typical conflicts: an
   action requested in a chat or email that the rules say belongs in the
   portal; a name in the wrong language; a lookup that would need
   normalization; a feature an external system already provides.
4. **Locate.** Which module or area, which plan and phase it belongs to,
   and which components it touches: backend service, frontend, database,
   external systems, notifications. Say what would have to change in
   each, at the level of "a new tool and a panel page", not a design.
5. **Size and risk.** S, M or L with a one-line reason each for size, the
   main risk, and any dependency it waits on. Never estimate in hours or
   days.
6. **Questions, written twice — once to be answered, once to be
   justified.** Only questions whose answer changes the design or the
   size. Never ask what the repo already answers, and never repeat a
   question a comment already answered.

   Each question gets two lines, and the order matters because the first
   is the one that has to travel:

   - **The question itself**, in the language of the person who has to
     answer it. No file paths, no table or column names, no task numbers,
     no English identifiers for a Spanish-speaking requester. Someone
     forwards this line to WhatsApp and it has to make sense alone. Write
     it so it can be answered out loud, in one breath, without opening
     anything. If the honest question needs a choice spelled out, spell
     the options out in their terms — *«¿lo querés en Excel de verdad, o
     te sirve el archivo simple que ya bajan los otros reportes?»*, not
     *«¿.xlsx o CSV?»*.
   - **Why it matters**, for the issue. Here go the paths, the task
     numbers, the measured risk, what breaks if the answer goes each way.
     This line is for whoever builds it, not for whoever answers.

   Name the answerer. Split maintainer questions (technical or priority
   calls, decisions about the repo's own rules) from requester questions
   (what they actually need, edge cases they have seen). Use this exact
   shape, because a digest across several issues is built by matching it:

   ```markdown
   - **Para <nombre> —** <la pregunta, contestable sin abrir nada>
     _Por qué importa:_ <rutas, números de tarea, riesgo medido>
   ```

   **Why this is a rule and not a style note.** Measured on 2026-09-19:
   three analyses produced nine questions for a requester who does not
   read the repo, every one of them written in repo terms — *«¿son
   `Department` o `getCategoryUID` de SENAITE?»*. Someone had to
   translate all nine by hand before they could be asked, and translate
   the answers back. The analysis was the cheap part of that day; moving
   the questions was the expensive part.
7. **Draft the plan task.** Written in the plan's own format and language,
   numbered as the next task of the phase it belongs to (or noting that a
   new phase is needed and why), ready to paste. It cites the issue and
   the source note ids. Prose scoping first, then the checkbox line, if
   that is how the plan does it.
8. **Recommend.** One of: *approve as is*, *approve with the variant
   above*, *needs the answers above first*, *already exists as N.N*, or
   *reject, because …*. One sentence of reason.

## Writing to the issue

The issue body has two sections delimited by HTML comments. You own one.

```
<!-- requerimiento -->
… the requester's / maintainer's text — never edit …
<!-- /requerimiento -->

<!-- analisis -->
… yours — replace in full on every run …
<!-- /analisis -->
```

- Replace everything between `<!-- analisis -->` and `<!-- /analisis -->`
  with the new analysis. If the markers are missing, append the section
  with markers at the end of the body. Never touch anything else in the
  body, not even to fix a typo.
- **Read the body, edit the substring, write the whole thing back — and
  read it back to check.** The requirement section is often the only copy
  of what someone said; a voice note that was transcribed once and pasted
  here may exist nowhere else. So: fetch the current body to a file,
  replace only the span between the analysis markers, write the file back,
  then fetch it again and confirm the requirement section survived
  verbatim. If it did not, restore it from what you read and say so in
  your comment.
- **Never write placeholder, probe or test content to a real issue.** Not
  "test", not "wip", not a short string to see whether editing works —
  editing works, and if it did not, the failure is visible in the command
  output. Measured on 2026-09-19: a run replaced an entire issue body with
  the string `short test body update`, destroying a requester's verbatim
  transcript and a full analysis; it was recoverable only because a copy
  happened to exist outside GitHub. There is no draft mode here. Every
  write lands on the thing people are reading.
- Post one **short comment** with what changed since the previous
  analysis (first run: "Análisis inicial" plus the recommendation and the
  open questions). This is what notifies the maintainer; keep it to a few
  lines. Do not paste the whole analysis in the comment.
- Keep a **Historial** at the end of your section: one line per run with
  the date and what changed.
- Labels: when done, remove `req:analizar`, add `req:analizado`; if there
  are open questions, also add `req:aclarar`. If the repo has module
  labels (for example `mod:rrhh`, `mod:tecnico`), add the one you located.
  Never add or remove `req:aprobado` or close the issue — those are the
  maintainer's.
- Write the analysis in the language the repo's plans are written in.
  Identifiers, file paths and labels stay as they are in the repo.

## Handoff of an approved issue

When invoked on an issue labeled `req:aprobado`:

1. Re-read the final requirement section and your last analysis; if they
   disagree, stop and comment asking which one is approved.
2. Add the task to the plan exactly as the repo's conventions say: the
   right file, the right section (for example the "now" section rather
   than a phase's history), the next number in its phase, prose scoping
   and checkbox in the plan's own style, citing the issue number and the
   source note ids. If the repo's rules say a new phase must be added in
   more than one place (an index file, a phases table), do all of them.

   **Work out the phase number yourself — and do not ask a human for it.**
   It is arithmetic, not judgement: the highest phase in use, plus one.
   What takes judgement is whether this opens a new phase at all or joins
   an existing one, and that you already decided in the analysis.

   Read **three** places, in this order, and take the maximum:

   - every plan of the repo, on the default branch;
   - every journal, because a closed phase keeps its number forever and
     numbers are never reused;
   - **the open pull requests**, because a handoff that has not merged yet
     is invisible to the first two and is exactly how two requirements end
     up claiming the same number. Measured on 2026-09-19: two
     requirements approved minutes apart both wanted phase 39; it only
     came out right because one of them happened to read the other's
     issue. Do not rely on happening to notice.

   Say in the PR body which number you took and how you got it — the
   highest you found, where, and that you checked open PRs. A number with
   its derivation can be checked in ten seconds by whoever reviews; a bare
   number cannot.

   If a human already stated a number (in a comment or a project field),
   use theirs and say so; a person who names a number has a reason you
   cannot see.
3. Open a pull request on a branch named after the task; never push to
   the default branch. The PR title names the task number; the body links
   the issue. Do not start implementing.

   **Never write `Closes #N`, `Fixes #N` or `Resolves #N` in that PR.**
   Merging it means the task reached the plan, not that the requester got
   anything. Measured on 2026-09-19: a handoff PR carried `Closes`, the
   merge closed the issue, and a request that was still blocked waiting on
   server access vanished from the board and from every open-questions
   listing while it was still pending. Link the issue with a bare URL or
   `Ref #N` instead. The issue closes when the thing exists, and a person
   closes it.
4. Comment the PR link on the issue **naming the task number in the first
   line** — `req:en-plan` is useless if it does not say *which* task, and
   the number is how anyone jumps from the request to the plan that now
   owns its state. Replace `req:aprobado` with `req:en-plan`.

   **Then put the task number in the issue title**, as a leading
   `[39.1] ` prefix (several tasks: `[39.2, 40.2] `). The title is what a
   Project card shows, so this is what makes the board answer "which task
   is this?" without opening anything. Keep the rest of the title exactly
   as it was — this is the one edit to the title the method allows, and
   only at handoff. And write the issue number in the plan task's own
   title line, right after the dash: `**39.1 — #189 · Vista de…**`. After
   the dash, not before it: every parser in the target repo anchors up to
   `**n.n —` and treats the rest as text. The `(issue #N` citation stays
   in the prose as well; that one is for the machines.
5. **Flag it if the task cannot be worked yet.** You know which section
   you wrote it into. If it went to the plan's waiting section (`Esperando`
   or whatever that plan calls it), also add `req:esperando`, and say in
   the same comment what it waits on and who owns that — copied from the
   plan, not invented. If it went to the actionable section, do not add the
   flag.

   The flag is a pointer, never a second copy: the condition and the owner
   live once, in the plan's own waiting line. Say where to look; do not
   restate the reasoning. And nothing removes this flag automatically — it
   comes off when someone moves the task into the actionable section, in
   the same change, by hand.

## What not to do

- Do not summarize without searching. An analysis with no prior-art
  section is not finished, and "I found nothing" is only a finding once
  you have searched the default branch rather than the working tree.
- Do not report an empty prior-art search without saying what you
  searched for — the words, the synonyms, the note ids, the files. A bare
  "nothing found" cannot be checked by the person reading it.
- Do not invent scope the requester did not ask for, and do not shrink it
  to what is easy. If part of it is blocked, say which part and why.
- Do not answer on the requester's behalf. If it depends on what they
  meant, it is a question for them.
- Do not decide. The recommendation is yours; the decision is a label the
  maintainer sets.
- Do not edit the requirement section, the title (except the `[n.n]`
  prefix the handoff adds, step 4), or other people's
  comments. Do not replace the body wholesale — splice your section into
  it. A body write that does not carry the requirement section forward
  unchanged is a bug, whatever else it got right.
- Do not open PRs or branches during analysis. Only the handoff does, and
  only against a non-default branch.

## Analysis template

```markdown
<!-- analisis -->
### Análisis

**Pedido.** <one paragraph, requester's terms, who asked, source note ids>

**Ya existe.** <task numbers / files / issues, or "No encontré nada que lo cubra: busqué …">

**Reglas.** <one bullet per applicable rule: complies / conflicts / variant>

**Dónde cae.** Módulo <…> · plan <…> · fase <…> · toca: <backend / portal / DB / externos>

**Tamaño y riesgo.** <S|M|L> — <reason>. Riesgo: <…>. Depende de: <…>.

**Preguntas.**
- **Para <maintainer> —** <pregunta en lenguaje llano, contestable sin abrir el repo>
  _Por qué importa:_ <rutas, números de tarea, riesgo medido>
- **Para <requester> —** <pregunta en sus términos, sin rutas ni nombres de tabla>
  _Por qué importa:_ <…>

**Tarea propuesta para el plan.**
<the task text in the plan's format, ready to paste>

**Recomendación.** <one of the five outcomes> — <one sentence>

**Historial.**
- <YYYY-MM-DD> Análisis inicial.
<!-- /analisis -->
```
