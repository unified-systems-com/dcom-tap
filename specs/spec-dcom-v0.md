# dcom Plugin Specification

**dcom** — the *design · configuration · operation model*, shipped as a set of dimension nodes.

## Plugin Identity

| Field | Value |
| --- | --- |
| Slug | `dcom` |
| Display name | TAP dcom |
| Description | The design / configuration / operation model as a dimension pack. |
| Kind | Vocabulary substrate: dimension nodes only. No models, no edges, no collector, no pages, no credential, no dependencies. |

**Default dimensions** (on every node this plugin ships)

| Dimension | Value | Why |
| --- | --- | --- |
| `tap.meta` | `dimension` | Core's `dimension` type stamps it. The pack's nodes carry no `dcom` value: they are the dictionary, not entries in it. |

## Philosophy

Every designed system produces three kinds of fact, and they age differently: what was *intended* (edited),
what is *declared to the system* (versioned; changes under you), and what *happened* (immutable). On a graph
they look alike. `dcom` is the one label that tells them apart, defined once here so every plugin that
models a designed system says it the same way. How a plugin adopts a dimension pack, and whether it must, is
the plugin management system's concern, not this plugin's.

## Goals

| # | Name | Description |
| --- | --- | --- |
| 1 | One Vocabulary | One key, three values, defined in one place. |
| 2 | Legible To Player 3 | Each value is a node on the grid with a description written for an AI reader. |

## Requirements

| RID | Name | Status | Notes |
| --- | --- | :---: | --- |
| req-dcom-model | [The Model](#the-model) | Proposed | Key `dcom`; values `design`, `configuration`, `operation`; the meaning of each |
| req-dcom-pack | [The Dimension Pack](#the-dimension-pack) | Proposed | Four `dimension` nodes in one GRIFT bundle; dotted names; no edges |

### The Model
----
RID: `req-dcom-model`

Status: `Proposed`

The label key is `dcom`. It takes exactly one of three string values. The value is a property of the
observation, not of the thing observed: a pipeline's definition is `configuration`; each run of it is an
`operation`. Nothing carries both.

| Value | Meaning | Mutability |
| --- | --- | --- |
| `design` | Intent that precedes any concrete instance: what the system is meant to do, as authored by people. | Edited; a rewrite supersedes it. |
| `configuration` | A declared instance the system reads to decide what may happen. | Versioned; changes under you, and facts derived from an older version may no longer hold. |
| `operation` | Something that happened: an execution, a scan, a finding emitted at a moment. | Immutable once recorded; a later occurrence is a new operation. |

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-model-1 | Key And Values Fixed | Proposed | The key is `dcom`; the value set is exactly `design`, `configuration`, `operation`, lower case. | |
| req-dcom-model-2 | Observation, Not Thing | Proposed | The value describes the observation; no entity carries two values. | |

### The Dimension Pack
----
RID: `req-dcom-pack`

Status: `Proposed`

`grift/dimensions.grift.json` seeds four nodes of core's `dimension` type and nothing else. Names are dotted:
the model is `dcom`, each value is `dcom.<value>`. There are no edges between them — parent and children
are derived from the name (`STARTS_WITH "dcom."` lists the values), and a value segment never contains a dot.

| Name | Description (verbatim; written for an AI reader) |
| --- | --- |
| `dcom` | The design / configuration / operation model. A node or edge describing a designed system may carry one `dcom` label saying which kind of fact it is: `design` (intent, edited), `configuration` (declared to the system, versioned, changes under you), or `operation` (happened, immutable). One value or none, never two. The value describes the observation, not the thing: a pipeline's definition is configuration; each run of it is an operation. Only facts derived from configuration can go stale, because only configuration changes. The values are the nodes `dcom.design`, `dcom.configuration`, `dcom.operation`. |
| `dcom.design` | The `design` position in the dcom model: intent that precedes any concrete instance — what a system is meant to do, as authored by people. Edited, not versioned by the system it describes; a rewrite supersedes it. The moment a design is encoded where the system reads it, that encoding is `configuration`. |
| `dcom.configuration` | The `configuration` position in the dcom model: a declared instance a system reads to decide what may happen — a definition file, a job as declared, a protection rule, a selector for where work may run. It has history: each change is a new version of the same node, and a fact derived from an older version's content (a reference, a line number, a permission) may no longer hold. Ask "is this still true?" of configuration. |
| `dcom.operation` | The `operation` position in the dcom model: something that happened — a run, an execution, a scan, a finding emitted at a moment in time. Immutable once recorded; observed again but never changed; a later occurrence is a later operation. Its status or conclusion are fields on it, not changes to it. Facts derived from an operation never go stale. Ask "did this happen, and how did it end?" of an operation. |

Entity ids are minted once (`scripts/uuid7`) and never change; the batch id and version move on every edit
of the bundle.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-pack-1 | Four Nodes | Proposed | Importing the bundle yields exactly four `dimension` nodes named `dcom`, `dcom.design`, `dcom.configuration`, `dcom.operation`, and no edges. | |
| req-dcom-pack-2 | Descriptions Present | Proposed | Each node's description is non-empty and names its own value. | The table above is the source; the test checks the property, not a byte-match. |
| req-dcom-pack-3 | Dictionary Carries No Value | Proposed | None of the four nodes has a `dcom` key in its dimensions. | |

## Reference data

| Document | Contents | Seeded by |
| --- | --- | --- |
| `grift/dimensions.grift.json` | The four dimension nodes (`req-dcom-pack`) | Every record |
