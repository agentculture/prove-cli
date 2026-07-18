# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`prove-cli` is an **AgentCulture mesh agent** scaffolded from `culture-agent-template`.
Its declared domain (`pyproject.toml`, `README.md`) is *"Agent/CLI for theorem
proving and formal verification"* — but **none of that domain code exists yet.**
What is here today is the template's baseline, unchanged:

- An **agent-first CLI** (identity/introspection verbs only — `whoami`, `learn`,
  `explain`, `overview`, `doctor`) cited from [teken](https://github.com/agentculture/teken)'s
  `afi-cli` `python-cli` reference.
- A **mesh identity** (`culture.yaml` + this `CLAUDE.md`).
- The **guildmaster skill kit** (18 skills under `.claude/skills/`, vendored
  cite-don't-import — see `docs/skill-sources.md`).
- A **build/deploy baseline** (pytest, lint, the agent-first rubric gate, PyPI
  Trusted Publishing).

So: when asked to build the actual theorem-proving/verification functionality,
you are adding the *first* domain code to a scaffold, not extending an existing
feature set. Add new nouns/verbs following the CLI pattern below.

## The `prove` vs `prove-cli` naming split (read this first)

Three different names are in play — do not conflate them:

| Thing | Name | Where |
|-------|------|-------|
| Python **package** (import) | `prove` | `prove/`, `import prove` |
| **Distribution** / PyPI name | `prove-cli` | `pyproject.toml [project].name`, SonarCloud key |
| Installed **console command** | `prove` | `pyproject.toml [project.scripts]`: `prove = "prove.cli:main"` |
| Internal `prog=` (help/error text) | `prove-cli` | `_build_parser()`, catalog, `learn` text |

**Gotcha:** the README and every in-CLI help/`learn`/`explain` string say
`prove-cli whoami`, but there is no `prove-cli` console script. The real command
is `uv run prove whoami`. `uv run prove-cli …` fails with "Failed to spawn".
This is a leftover from an incomplete template rename; the help-text `prog` was
never reconciled with the `[project.scripts]` name. When documenting or invoking,
use `prove`; treat the `prove-cli` strings in output as cosmetic.

## Commands

```bash
uv sync                                    # install deps + dev group into .venv
uv run prove whoami                        # run the CLI (command is `prove`)
uv run pytest -n auto                      # full suite, parallel (xdist)
uv run pytest tests/test_cli.py::test_whoami_text -v   # a single test
uv run pytest -n auto --cov=prove --cov-report=term    # with coverage (gate: fail_under=60)
```

Lint (all four run in CI; must pass before merge):

```bash
uv run black --check prove tests
uv run isort --check-only prove tests
uv run flake8 prove tests
uv run bandit -c pyproject.toml -r prove
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills" "#.teken"
```

The **agent-first rubric gate** (a distinct CI job — this is not a normal linter):

```bash
uv run teken cli doctor . --strict         # the seven-bundle afi-cli rubric
```

`teken` is a **dev-only** dependency; the runtime package has `dependencies = []`
and must stay dependency-free (it's cite-don't-import from `afi-cli`, not a
library install). Don't add runtime deps without a deliberate reason.

## CLI architecture

The whole CLI is a thin argparse dispatcher with two hard contracts (error
handling and output streams) that every command must honor. The pieces span
several files — understand the flow before editing any one of them.

**Dispatch flow** (`prove/cli/__init__.py`):
`main(argv)` → `_build_parser()` registers each command → `parse_args` →
`_dispatch(args)` calls `args.func(args)`. A handler returns `None`/`int` on
success; **failures raise `CliError`**, never return an error code directly.

**Error contract** (`prove/cli/_errors.py` + `_output.py`): every failure is a
`CliError(code, message, remediation)`. `_dispatch` catches `CliError` (and wraps
any stray exception into one) so **no Python traceback ever reaches stderr**.
Errors render as `error: <msg>` / `hint: <remediation>` in text mode — the
`hint:` prefix is *required* by the agent-first rubric. Argparse's own errors
(unknown verb, bad flag) are routed through the same format by
`_CliArgumentParser.error()`, which overrides argparse's default
`prog: error:` / exit-2 behavior. The subparsers are built with `parser_class=_CliArgumentParser`
so this propagates to nested nouns (see `cli.py`'s `noun_sub`).

**JSON before parse:** parse-time errors happen before `args.json` exists, so
`main()` pre-scans raw argv for `--json` and stashes it in
`_CliArgumentParser._json_hint` (class-level, shared across subparsers) so even
argparse errors honor JSON mode.

**Output contract** (`prove/cli/_output.py`): **results → stdout, errors/
diagnostics → stderr, never mixed.** Use `emit_result` / `emit_error` /
`emit_diagnostic`; don't `print()`. Every command takes `--json`.

**Exit codes:** `0` success, `1` user error, `2` environment error, `3+`
reserved. Centralized in `_errors.py`; don't invent ad-hoc codes.

**`explain` catalog** (`prove/explain/catalog.py`, `__init__.py`): markdown docs
keyed by command-path tuples (`("whoami",)`, `("cli","overview")`). `resolve()`
raises `CliError` on an unknown path. The test `test_every_catalog_path_resolves`
walks `known_paths()` — **every catalog entry must resolve**, so keep `ENTRIES`
consistent with what you register.

### Adding a verb or noun group

1. Create `prove/cli/_commands/<name>.py` exposing `register(sub)` (build the
   subparser, add `--json`, `p.set_defaults(func=…)`).
2. Wire it into `_build_parser()` in `prove/cli/__init__.py` (there's a marked
   "Register your own noun groups here" spot).
3. Add a matching entry to `prove/explain/catalog.py` `ENTRIES`.
4. Honor both contracts: emit via `_output`, raise `CliError` on failure.
5. **Rubric rule:** any *noun* that has action-verbs must also expose an
   `overview` sub-verb (`overview_cli_noun_exists`). The `cli` noun exists solely
   to satisfy this — copy its shape (`prove/cli/_commands/cli.py`).

## Identity & `doctor` invariants

Identity comes from `culture.yaml` (`suffix: prove-cli`, `backend: claude`),
parsed **without a YAML dependency** by a hand-rolled reader in `whoami.py`
(`read_agent_fields`) that walks up from `__file__` to find the repo's own
`culture.yaml` (not the CWD's). Keep that parser tolerant of the documented
`- suffix:` / `backend:` / `model:` shape only.

`doctor` mirrors the invariants `steward doctor` enforces on a mesh agent:

- **backend-consistency / prompt-file-present** — `backend` maps to a required
  prompt file: `claude → CLAUDE.md`, `acp → AGENTS.md`, `gemini → GEMINI.md`
  (`_PROMPT_FILE` in `doctor.py`). This file existing is *load-bearing* — don't
  delete `CLAUDE.md`; edit it.
- **skills-present** — `.claude/skills/` must be non-empty.

When run from a wheel install (no `culture.yaml` beside the package) both
`whoami` and `doctor` degrade to defaults / a single info check and exit 0.

## Contribution workflow (AgentCulture rules)

- **Every PR bumps the version — even docs/CI/config-only PRs.** The
  `version-check` CI job fails a PR whose `pyproject.toml` version equals `main`'s.
  Use the `version-bump` skill (updates `pyproject.toml` + prepends a
  Keep-a-Changelog entry to `CHANGELOG.md`).
- Use the **`cicd` skill** for the PR lifecycle (create, read review, reply,
  poll SonarCloud gate); it delegates to `devex pr` and adds Sonar `status` /
  `await`. CI gates on the SonarCloud quality gate when `SONAR_TOKEN` is set
  (token-less repos / fork PRs stay green).
- CI (`.github/workflows/tests.yml`): `test` (pytest + coverage + Sonar), `lint`
  (black/isort/flake8/bandit/markdownlint + the rubric gate), `version-check`.
  `publish.yml` does TestPyPI on PRs and PyPI on push to `main` via Trusted
  Publishing (only when `pyproject.toml` or `prove/**` changed).

## Skills (cite-don't-import)

The 18 skills under `.claude/skills/` are **vendored copies**, not authored here —
provenance and the exact re-sync procedure live in `docs/skill-sources.md`. Most
come from **guildmaster**; `ask-colleague` is vendored directly from the
`colleague` checkout (a tracked divergence pending guildmaster's re-broadcast).
Rules when touching them:

- Every `SKILL.md` **must carry `type: command`** in frontmatter — the culture
  `core.skill_loader` silently skips any skill without it.
- **Don't edit script bodies** — re-sync from upstream instead (per
  `docs/skill-sources.md`). Only consumer-identifying prose and the `type:` field
  are adapted locally; two exceptions (`agex`→`devex`, `outsource`→`ask-colleague`)
  are documented as tracked in-place divergences.

## Conventions and workflow

**Memory discipline — recall before, remember after.** This repo keeps its
eidetic memory **in-repo and public**: records resolve to
`<repo-root>/.eidetic/memory` — committed, and shared with the team and mesh
peers (the `claude` and `colleague` backends both read the same
`prove-cli` scope), so memory travels with the repo, not a private
home-dir store. Make it a per-task habit:

- **`/recall` before you start.** Search the store for the area you're about
  to touch — prior decisions, gotchas, "have we done this before?" — so you
  build on what's already known instead of re-deriving it. Do this before
  non-trivial tasks, not just when asked.
- **`/remember` when something worth keeping surfaces.** A non-obvious
  decision and its rationale, a constraint, a fix and *why* it was needed, a
  gotcha that cost time, a fact the next session would otherwise re-learn.
  Capture it as it happens, not at the end when it's faded.

A plain `/remember` lands the note in `./.eidetic/memory` in this repo — no
flag needed (the wrappers here default to `--visibility public`; in-repo
routing needs `eidetic >= 0.10.0`, older CLIs keep records in `$HOME`). Keep
something out of the committed store only by passing `--visibility private`
(routes to `$HOME/.eidetic/memory`, never committed); `/recall` reads both
stores and merges. Don't store what the repo already records (code structure,
git history, what's already in this file or `CHANGELOG.md`) — store what you'd
have to re-derive. These are the `recall`/`remember` skills (`.claude/skills/`),
backed by the `eidetic` store.

## Renaming this template

The template name is hard-coded in ~100 places (package, dist, CLI strings,
`_ISSUES_URL`, tests, `sonar-project.properties`, README). If forking this into a
differently-named agent, `README.md`'s "Make it your own" section is the
procedure; discover occurrences with `git grep -n prove-cli` / `git grep -n prove`.
Note that a *proper* rename should also fix the `prove` vs `prove-cli` console-
script split described above, which the template currently ships broken.
