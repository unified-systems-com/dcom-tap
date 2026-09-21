# dcom-tap

**TAP dcom plugin — the design · configuration · operation axis as a dimension pack.**

One axis, three positions, for anything a designed system produces. `dcom` puts that axis on
the grid as a vocabulary other plugins inherit, so a reader — human or AI — can tell which
*kind* of fact a node is before asking anything else of it.

## What this plugin owns

- Four `dimension` nodes: `dcom`, `dcom.design`, `dcom.configuration`, `dcom.operation`, each
  carrying a description written for an AI reader. They ship in one GRIFT bundle,
  `tap_plugin/dcom/grift/dimensions.grift.json`.
- The rules for stamping the `dcom` label on nodes and edges, and what carrying a value promises.

It has no models, no edges, no pages, no collector, no credential and no network. The four pack
nodes are the *dictionary*: they carry `tap.meta: dimension` and no `dcom` value of their own.

## The axis in one table

| Value | It is | It behaves |
| --- | --- | --- |
| `design` | Intent, as authored by people, before any concrete instance. | Edited. A rewrite supersedes it. |
| `configuration` | A declared instance the system reads to decide what may happen. | Versioned. It changes under you, so facts derived from its content can go stale. |
| `operation` | Something that happened — a run, a scan, a finding at a moment. | Immutable. Derivations from it never go stale. |

An entity carries one value or none, never two, and the value describes the **observation**, not
the thing: a pipeline's definition is `configuration`; each run of it is an `operation`.

## Inheriting the axis

Two lines in files the inheriting plugin already owns:

1. `depends_on = [{ slug = "dcom", note = "…" }]` in its `tap-plugin.toml`.
2. `"dcom": "<value>"` in each node type's `DEFAULT_DIMENSIONS`, and in each edge file's
   `default_dimensions`.

A type deliberately left unstamped is named, with its reason, in the inheriting plugin's own spec.
Silence is an omission, not an exemption.

## Read first

- `specs/spec-dcom-v0.md` — the plugin specification. It is the contract; this README is a summary.

## Standing it up

The in-package `ci` boot record installs this plugin alone and seeds the pack — the stack its own
tests run in, offline and credential-free:

```
scripts/spawn-session.sh <label> \
  --from 'git+https://github.com/unified-systems-com/dcom-tap@<rev>#ci' \
  --dev-plugins dcom
```

Then, in that stack:

```
scripts/dc exec -T web uv run python -m tap_plugins.validate_plugin /app/_dev-plugins/dcom --strict
scripts/dc exec -T web uv run pytest --pyargs tap_plugin.dcom
```
