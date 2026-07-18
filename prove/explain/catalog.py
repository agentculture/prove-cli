"""Markdown catalog for ``prove-cli explain <path>``.

Each entry is verbatim markdown. Keys are command-path tuples. The empty tuple
and ``("prove-cli",)`` both resolve to the root entry.

Keep bodies self-contained: an agent reading one entry should get enough
context without chaining reads.
"""

from __future__ import annotations

_ROOT = """\
# prove-cli

A clonable template for AgentCulture mesh agents. It carries an agent-first CLI
(cited from the teken `python-cli` reference), a mesh identity (`culture.yaml` +
`CLAUDE.md`), the canonical guildmaster skill kit under `.claude/skills/`, and a
buildable/deployable package baseline. Clone it, rename the package, edit
`culture.yaml`, and you have a new agent.

## Verbs

- `prove-cli whoami` — identity probe from `culture.yaml`.
- `prove-cli learn` — structured self-teaching prompt.
- `prove-cli explain <path>` — markdown docs for any noun/verb.
- `prove-cli overview` — descriptive snapshot of the agent.
- `prove-cli doctor` — check the agent-identity invariants.
- `prove-cli cli overview` — describe the CLI surface.

## Exit-code policy

- `0` success
- `1` user-input error
- `2` environment / setup error
- `3+` reserved

## See also

- `prove-cli explain whoami`
- `prove-cli explain doctor`
"""

_WHOAMI = """\
# prove-cli whoami

Reports the agent's identity from `culture.yaml`: nick (`suffix`), backend,
served model, and the package version. Read-only.

## Usage

    prove-cli whoami
    prove-cli whoami --json
"""

_LEARN = """\
# prove-cli learn

Prints a structured self-teaching prompt covering purpose, command map,
exit-code policy, `--json` support, and the `explain` pointer.

## Usage

    prove-cli learn
    prove-cli learn --json
"""

_EXPLAIN = """\
# prove-cli explain <path>

Prints markdown documentation for any noun/verb path. Unlike `--help` (terse,
positional), `explain` is global and addressable by path.

## Usage

    prove-cli explain prove-cli
    prove-cli explain whoami
    prove-cli explain --json <path>
"""

_OVERVIEW = """\
# prove-cli overview

Read-only descriptive snapshot of the agent: identity (from `culture.yaml`), the
verb surface, and the sibling-pattern artifacts the template carries. Accepts an
ignored `target` so a stray path never hard-fails.

## Usage

    prove-cli overview
    prove-cli overview --json
"""

_DOCTOR = """\
# prove-cli doctor

Checks the agent-identity invariants `steward doctor` verifies:
prompt-file-present and backend-consistency (`claude` → `CLAUDE.md`), plus a
skills-present check. Exits 1 when unhealthy.

## Usage

    prove-cli doctor
    prove-cli doctor --json
"""

_CLI = """\
# prove-cli cli

Noun group for CLI-surface introspection. `cli overview` describes the CLI
itself (distinct from the global `overview`, which describes the agent).

## Usage

    prove-cli cli overview
    prove-cli cli overview --json
"""


ENTRIES: dict[tuple[str, ...], str] = {
    (): _ROOT,
    # Both the distribution name (`prove-cli`) and the installed console command
    # (`prove`, from [project.scripts]) resolve to the root entry, so `explain
    # prove` and `explain prove-cli` both work. The agent-first rubric probes
    # `explain <console-command>`, i.e. `explain prove`.
    ("prove-cli",): _ROOT,
    ("prove",): _ROOT,
    ("whoami",): _WHOAMI,
    ("learn",): _LEARN,
    ("explain",): _EXPLAIN,
    ("overview",): _OVERVIEW,
    ("doctor",): _DOCTOR,
    ("cli",): _CLI,
    ("cli", "overview"): _CLI,
}
