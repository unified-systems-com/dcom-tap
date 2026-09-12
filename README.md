# tap-plugin-dcom

**TAP dcom plugin — the design · configuration · operation axis as a dimension pack.**

> Status: specification only (2026-09-12). Nothing ships yet; the spec is the plan.

## What this plugin owns

- Four dimension nodes: `dcom`, `dcom.design`, `dcom.configuration`, `dcom.operation`, each carrying a
  description written for an AI reader.
- The rules for stamping the `dcom` label on nodes and edges, and what carrying a value promises.

It has no models, no collector, no pages and no credential. Other plugins inherit the axis by declaring
`dcom` in `depends_on` and stamping the label on the types they own.

## Read first

- `specs/spec-dcom-v0.md` — the plugin specification.
