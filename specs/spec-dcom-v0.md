# dcom Plugin Specification

**dcom** — the *design · configuration · operation model*. One dimension, three positions, for anything a
designed system produces. This plugin puts that model on the grid as a vocabulary other plugins inherit.

## Plugin Identity

| Field | Value |
| --- | --- |
| Slug | `dcom` |
| Display name | TAP dcom |
| Description | The design / configuration / operation model as a dimension pack: four dimension nodes and the rules for stamping the `dcom` label on nodes and edges. |
| Kind | Vocabulary substrate (like a `*_core`, but with no models of its own): ships dimension nodes and rules. No collector, no pages, no credential, no network. |
| Dist | `dcom-tap` |
| Import namespace | `tap_plugin.dcom` |
| Entry point | `dcom = "tap_plugin.dcom.apps:DcomConfig"` under `[project.entry-points."tap.plugins"]` |
| AppConfig | `tap_plugin.dcom.apps.DcomConfig` (Django dotted path; `name` derived from the module path, `label` / `verbose_name` from the manifest) |
| Repo | `unified-systems-com/dcom-tap`, standalone from the first commit (every plugin is evicted) |
| Dev workspace | `spawn-session.sh <label> --from <record> --dev-plugins dcom` |
| Depends on | Nothing. Core's `dimension` type is the only type this plugin writes. |
| Inherited by | Any plugin that declares `dcom` in `depends_on` and stamps the label on the types it owns (`req-dcom-inheritance`). |
| Collector | None. The pack is seeded, never collected. |
| Pages | None in v0. |
| GRIFT | `grift/dimensions.grift.json` — the dimension pack (`req-dcom-pack`) |
| Boot records | `ci` (in-package, `req-boot-bootstrap-ci-record`): installs this plugin alone, seeds the pack, and is the stack the plugin's own tests run in — `req-dcom-record` |
| Spec home | This file, at the repository root `specs/`, from the first commit. Core is never edited to define dcom. |

**Default dimensions** (on every node this plugin ships)

| Dimension | Value | Why |
| --- | --- | --- |
| `tap.meta` | `dimension` | Core's `Dimension` type stamps it. The pack's nodes are the dictionary, not entries in it, and carry no `dcom` value themselves. |

## Philosophy

Every designed system has three kinds of fact about it, and they age differently.

There is what was *intended*: a design, a policy as authored, an architecture. It is edited, argued over,
and superseded. There is what is *declared to the system*: the file, the setting, the rule that the system
actually reads to decide what may happen. It has history; it changes under you; the version that was true
last week is not the version that is true now. And there is what *happened*: the run, the scan, the
execution, the finding a tool emitted at a moment in time. It never changes, because it already occurred.

These three do not look different on a graph. A workflow file and a run of that workflow are both nodes with
a name and a timestamp. A policy and the enforcement of it are both nodes with a repository beside them. A
reader — human or AI — who cannot tell which kind of fact a node is will ask the wrong question of it: "is
this still true?" of a run that cannot change, or "did this happen?" of a file that only says what may.

`dcom` makes the distinction a label every node and edge can carry, in one vocabulary shared by every plugin
that opts in. It is not universal: a thing that was never designed — a person, a place — has no
configuration and no operation, and a plugin that models such things leaves the label alone. For everything
TAP collects from designed systems, it is the first question to answer.

Two properties follow from the model and are the reason it exists as a shared vocabulary rather than a
convention each plugin re-invents:

- **Only configuration goes stale.** A fact derived from the *content* of a configuration node — a
  reference it contains, a line number in it, a permission it grants — was true for the version it was
  derived from. When that node changes, the derivation may no longer hold. A fact derived from an operation
  never needs re-checking, because operations do not change. The model is how the grid knows which
  derivations to re-examine, in one place, for every plugin at once.
- **One query reads a whole side of the grid.** "Everything that is declared" and "everything that
  happened" are each a single containment predicate across every plugin that inherits the model, with no
  enumeration of types.

The model is deliberately small: three values, one key, four nodes. Everything else a reader needs — what a
*particular* configuration means, how a *particular* operation ran — belongs to the plugin that owns the
type. dcom says which kind of fact it is, and stops.

**Provenance markers.** Nothing in this spec is *observed* yet; every claim is *designed*. The first
inheriting plugin's collection turns the containment queries in `req-dcom-queries` into observations.

## Goals

| # | Name | Description |
| --- | --- | --- |
| 1 | One Vocabulary | Every plugin that models a designed system says "declared" and "happened" the same way, with the same key and the same three values. |
| 2 | Legible To Player 3 | The model and each value are nodes on the grid with descriptions written for an AI reader, so the vocabulary is read from the grid, never inferred from a type name. |
| 3 | Derived, Not Stored | Parent, children and the label a node defines are all derived from its name. Nothing about the hierarchy is stored twice. |
| 4 | Opt-In | Inheriting the model is one manifest line; a plugin that does not inherit it is untouched. |
| 5 | Permissive First | v0 defines the rules and ships the pack; enforcement of stamping is a `Backlog` requirement, shaped after the rules have been used in the field. |

## Requirements

| RID | Name | Status | Notes |
| --- | --- | :---: | --- |
| req-dcom-model | [The Model](#the-model) | Proposed | Key `dcom`; values `design`, `configuration`, `operation`; the meaning and mutability of each |
| req-dcom-pack | [The Dimension Pack](#the-dimension-pack) | Proposed | Four `dimension` nodes, dotted names, descriptions for Player 3, no edges |
| req-dcom-naming | [Dotted Names Carry The Hierarchy](#dotted-names-carry-the-hierarchy) | Proposed | Parent, children and label are derived from the name |
| req-dcom-inheritance | [Inheriting The Model](#inheriting-the-model) | Proposed | `depends_on = dcom` is the opt-in; stamping via default dimensions on the plugin's own types |
| req-dcom-stamping | [Stamping Rules](#stamping-rules) | Proposed | One value or none; property of the observation; edges stamp from their type or their source |
| req-dcom-promises | [What A Value Promises](#what-a-value-promises) | Proposed | Configuration is versioned and can go stale; operation is immutable; design is edited |
| req-dcom-queries | [Canonical Queries](#canonical-queries) | Proposed | The Gryphon a reader uses to read a side of the grid or enumerate the model |
| req-dcom-record | [CI Record And Tests](#ci-record-and-tests) | Proposed | The `ci` boot record seeds the pack; tests prove the four nodes and the naming rules |
| req-dcom-mandatory | [Mandatory Stamping](#mandatory-stamping) | Backlog | A manifest surface naming the dimensions every type must carry, checked when the plugin is validated; shape to be dialled in after use |
| req-dcom-conformance | [Conformance As A Report](#conformance-as-a-report) | Backlog | Per plugin, per type: stamped / exempt with reason / omitted — computed, never declared |
| req-dcom-design | [Design On The Grid](#design-on-the-grid) | Backlog | Requirements and architecture as `design` nodes joined to the configuration that encodes them |
| req-dcom-nongoals | [v0 Non-Goals](#v0-non-goals) | Proposed | Edges between dimension nodes; deeper hierarchy; a `design` collector |

### The Model
----
RID: `req-dcom-model`

Status: `Proposed`

#### Implementation

The label key is `dcom`. It takes exactly one of three string values.

| Value | Meaning | Mutability | Examples |
| --- | --- | --- | --- |
| `design` | Intent that precedes any concrete instance: what the system is *meant* to do, as authored by people. | Edited. A design changes by being rewritten, and the rewrite supersedes it. | A requirement; an architecture; a policy as a document before it is encoded anywhere the system reads. |
| `configuration` | A declared instance the system *reads to decide what may happen*. | Versioned. It changes under you; each change is a new version of the same node, and facts derived from an older version may no longer hold. | A pipeline definition file; a job as declared in it; a protection rule on a branch or environment; a set of labels that selects where work may run; a secret's existence and scope. |
| `operation` | Something that *happened*: an execution, a scan, a measurement, a finding emitted at a moment. | Immutable once recorded. It can be re-observed, never changed; a later observation is a later operation. | A pipeline run; a job execution; a scanner run and each finding it produced; a deployment. |

The value is a property of the **observation**, not of the thing observed. The same pipeline appears as a
`configuration` node (its definition) and, separately, as `operation` nodes (its runs). Nothing carries both.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-model-1 | Key And Values Fixed | Proposed | The key is `dcom`; the value set is exactly `design`, `configuration`, `operation`, lower case. | |
| req-dcom-model-2 | Meaning Stated Per Value | Proposed | Each value's meaning and mutability rule is stated in this spec and in the corresponding node's description (`req-dcom-pack-3`). | |
| req-dcom-model-3 | Observation, Not Thing | Proposed | The spec states that the value describes the observation and that no entity carries two values. | |

### The Dimension Pack
----
RID: `req-dcom-pack`

Status: `Proposed`

#### Implementation

`grift/dimensions.grift.json` seeds four nodes of core's `dimension` type. Nothing else: no edges, no
pages, no searches.

| Name | Role | Description (verbatim; written for an AI reader) |
| --- | --- | --- |
| `dcom` | model | The design / configuration / operation model. Every node or edge that describes a designed system may carry one `dcom` label saying which kind of fact it is: `design` (intent, edited), `configuration` (declared to the system, versioned, changes under you), or `operation` (happened, immutable). An entity carries one value or none, never two. The value describes the observation, not the thing: a pipeline's definition is configuration; each run of it is an operation. Only facts derived from configuration can go stale, because only configuration changes. The three values are the nodes named `dcom.design`, `dcom.configuration` and `dcom.operation`. |
| `dcom.design` | value | The `design` position in the dcom model: intent that precedes any concrete instance — what a system is meant to do, as authored by people. A design is edited, not versioned by the system it describes; a rewrite supersedes it. Nothing the system reads at run time is a design; the moment a design is encoded where the system reads it, that encoding is `configuration`. |
| `dcom.configuration` | value | The `configuration` position in the dcom model: a declared instance that a system reads to decide what may happen — a definition file, a job as declared, a protection rule, a selector for where work may run. Configuration has history: it changes under you, each change is a new version of the same node, and any fact derived from the content of an older version (a reference it contained, a line it flagged, a permission it granted) may no longer hold. When you ask "is this still true?", ask it of configuration. |
| `dcom.operation` | value | The `operation` position in the dcom model: something that happened — a run, an execution, a scan, a finding emitted at a moment in time. An operation is immutable once recorded; it can be observed again but never changed, and a later occurrence is a later operation. Its status or conclusion are fields on it, not a change to it. Facts derived from an operation never go stale. When you ask "did this happen, and how did it end?", ask it of an operation. |

Every node carries `tap.meta: dimension` (core's default for the type) and **no** `dcom` value: the pack is
the dictionary, and dictionary entries are not entries in themselves.

Entity ids are minted once (`scripts/uuid7`) and never change; the batch id and version move on every edit
of the bundle, and description text is edited in place under a new batch so the ids stay stable.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-pack-1 | Four Nodes | Proposed | Importing the pack yields exactly four `dimension` nodes named `dcom`, `dcom.design`, `dcom.configuration`, `dcom.operation`. | |
| req-dcom-pack-2 | No Edges | Proposed | The bundle declares no edges. | `req-dcom-naming` makes them redundant. |
| req-dcom-pack-3 | Descriptions Present And Specific | Proposed | Each node's description is non-empty, names its own value, and for the three value nodes states the mutability rule. | The table above is the source; the test checks the properties, not a byte-match, so the prose can improve without a spec edit. |
| req-dcom-pack-4 | Dictionary Carries No Value | Proposed | None of the four nodes has a `dcom` key in its dimensions. | |

### Dotted Names Carry The Hierarchy
----
RID: `req-dcom-naming`

Status: `Proposed`

#### Implementation

Dimension nodes are flat peers. There is no parent/child edge and no container node. The hierarchy lives in
the name, the way it does in DNS and in package names, and everything about it is derived:

| Fact | Derivation |
| --- | --- |
| Parent of a node | Its name with the last dot-separated segment removed. `dcom.operation` → `dcom`. A name with no dot is a model and has no parent. |
| Values of a model | Every dimension node whose name starts with the model's name followed by a dot. |
| Label a value node defines | Key = everything before the last dot; value = the last segment. `dcom.configuration` defines the label `dcom: configuration`. |
| Depth | v0 defines one level: model and value. Deeper names are not forbidden by the `dimension` type but are not used by this pack and carry no defined meaning. |

One constraint makes the derivations unambiguous: **a value segment never contains a dot.**

This rule is stated here because dcom is the first dimension pack, and the next model anyone defines should
have the same shape. The rule is about *dimension node names*; it says nothing about which characters a
label key may contain in an entity's `dimensions` column.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-naming-1 | Prefix Enumerates Values | Proposed | `MATCH (d:dimension) WHERE d.name STARTS_WITH "dcom." RETURN d` returns exactly the three value nodes. | |
| req-dcom-naming-2 | Last Segment Is The Value | Proposed | For each value node, the last segment of its name equals a value in `req-dcom-model-1`, and the prefix equals `dcom`. | |
| req-dcom-naming-3 | No Dot In A Value | Proposed | No value node's last segment contains a dot. | |

### Inheriting The Model
----
RID: `req-dcom-inheritance`

Status: `Proposed`

#### Implementation

A plugin inherits dcom by doing two things, both in files it already owns:

1. **Declare it.** `depends_on = [{ slug = "dcom", note = "…" }]` in `tap-plugin.toml`. This is the opt-in
   and the conformance claim in one line: the plugin is saying every type it ships is either stamped or
   deliberately exempt. Because it is a real dependency, the pack is seeded before the plugin's own data
   lands, and the plugin's `ci` boot record installs dcom in its closure like any other dependency.
2. **Stamp it.** On each node type, `DEFAULT_DIMENSIONS` gains `"dcom": "<value>"`. On each edge type, the
   edge file's `default_dimensions` gains the same. The value is authored once per type, in the type's own
   declaration, and applied by core's default-dimension merge at create time. No collector code writes the
   key by hand, except in the one case `req-dcom-stamping-4` names.

A type the plugin decides **not** to stamp is exempt, and the plugin's own spec says so, per type, with the
reason. Silence is not exemption; it is an omission, and v0 tolerates it (Goal 5) without pretending it is
a decision.

The inheriting plugin's spec gains a **dcom** section listing every node and edge type with its value or its
exemption. That table is the plugin's statement of conformance until `req-dcom-conformance` derives it.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-inheritance-1 | Dependency Is The Opt-In | Proposed | The spec states that declaring `dcom` in `depends_on` is how a plugin inherits the model, and that no other manifest surface is required in v0. | |
| req-dcom-inheritance-2 | Stamp Via Defaults | Proposed | The spec states that the value is authored on the type's default dimensions and applied by core's merge, never written per-entity by collector code except under `req-dcom-stamping-4`. | |
| req-dcom-inheritance-3 | Exemption Is Stated | Proposed | The spec requires an inheriting plugin to list each unstamped type with a reason in its own spec. | |

### Stamping Rules
----
RID: `req-dcom-stamping`

Status: `Proposed`

#### Implementation

| # | Rule |
| --- | --- |
| 1 | **One value or none.** An entity carries at most one `dcom` label. There is no "both", and there is no value meaning "unknown"; an entity whose side is unknown carries no `dcom` key, which is distinguishable from every value. |
| 2 | **The observation, not the thing.** The same real-world object may appear as a `configuration` node and, separately, as `operation` nodes. They are different entities and are joined by an edge the owning plugin defines, never by sharing a value. |
| 3 | **Edges carry it from their type.** An edge type whose every instance sits on one side declares that value in `default_dimensions`. |
| 4 | **Mixed-source edge types stamp from the source endpoint.** An edge type whose sources span both sides declares no `dcom` default; the collector stamps each instance with its source node's value at emit time. This is the only case in which collector code writes the key. |
| 5 | **Not a lifecycle state, timestamp, confidence or provenance.** `operation` does not mean recent, finished or successful; those are fields on the node. Whether a link was observed or inferred is an edge property, not a dcom value. |
| 6 | **Dictionary nodes carry no value.** The four pack nodes, and any future dimension node, are stamped `tap.meta: dimension` and nothing from the model they define. |

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-stamping-1 | Rules Stated | Proposed | The six rules above appear in the spec and are cited by the inheriting plugins' dcom sections. | |
| req-dcom-stamping-2 | No Unknown Value | Proposed | The value set contains no sentinel for "unknown"; absence of the key is the third state. | Three states, never two: `configuration` / `operation` / not stamped. |

### What A Value Promises
----
RID: `req-dcom-promises`

Status: `Proposed`

#### Implementation

Carrying a value is a promise about how the node behaves over time, and core mechanisms may rely on it:

| Value | Promise | What may rely on it |
| --- | --- | --- |
| `design` | Changes by being rewritten; the system does not read it. | Nothing in v0. Named so the model is complete and so a design-side plugin has somewhere to land (`req-dcom-design`). |
| `configuration` | Changes under you and is versioned: each change is a new version of the same node, recorded as history on the spine. A fact derived from the node's *content* is true for the version it was derived from. | The grid's stale-derivation mechanism: an edge derived from a configuration node's content records the node version it was derived against and is marked potentially out of date when the node changes (`unified-systems-com/tap#447`). Only edges from `configuration` nodes enter that check. |
| `operation` | Immutable once recorded. A re-observation that finds the same operation is not a change; a later occurrence is a new node. | Anything that wants to skip re-checking: derivations from operations are never stale. Read models may cache them indefinitely. |

A plugin that stamps `configuration` on a type it then overwrites in place without a version, or `operation`
on a type it mutates, has broken the promise, and the failure will surface as a stale check that never fires
or a cache that is wrong. The promise is the reason to get the value right, and the reason
`req-dcom-mandatory` exists.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-promises-1 | Promises Stated | Proposed | The spec states the mutability promise of each value and names what may rely on it. | |
| req-dcom-promises-2 | Stale Check Scoped To Configuration | Proposed | The spec states that only derivations from `configuration` nodes are subject to the grid's stale-derivation check. | The mechanism itself is core's (tap#447), not this plugin's. |

### Canonical Queries
----
RID: `req-dcom-queries`

Status: `Proposed`

#### Implementation

The queries a reader — a panel, a test, an AI assistant — uses to read the model. Each runs against the
search role with no plugin-specific knowledge.

| Question | Gryphon |
| --- | --- |
| Everything declared, across every plugin | `MATCH (n) WHERE n.dimensions["dcom"] = "configuration" RETURN n` |
| Everything that happened | `MATCH (n) WHERE n.dimensions["dcom"] = "operation" RETURN n` |
| What the model means | `MATCH (d:dimension) WHERE d.name = "dcom" RETURN d` |
| What values it allows, with their meanings | `MATCH (d:dimension) WHERE d.name STARTS_WITH "dcom." RETURN d` |
| Nodes of a type that are not stamped (the third state) | `MATCH (n:<type>) WHERE n.dimensions["dcom"] IS NULL RETURN n` |

The last row is how conformance is *read* before anything *enforces* it: an inheriting plugin's test may
assert it returns nothing for each type its dcom section stamps.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-queries-1 | Queries Execute | Proposed | Each query above parses and executes against a grid with the pack seeded. | Proven in this plugin's tests for the two dictionary queries; the containment queries are proven by the first inheriting plugin. |

### CI Record And Tests
----
RID: `req-dcom-record`

Status: `Proposed`

#### Implementation

The in-package `ci` boot record (`tap_plugin/dcom/boot/ci.boot.json`) installs this plugin alone — it has
no dependencies — seeds the pack, and is the stack the plugin's own tests run in. Offline, credential-free,
no network. Reproduce CI exactly: `spawn-session.sh <label> --from 'git+https://github.com/unified-systems-com/dcom-tap@<rev>#ci' --dev-plugins dcom`.

Tests ship inside the package (`tap_plugin/dcom/tests/`) so they ride the wheel and run against any install:

| Test | Proves |
| --- | --- |
| `test_dcom_manifest.py` | Identity chain (slug, dist `dcom-tap`, namespace, entry point) agrees; no `[models]`, no `[edges]`, one `[grift]` entry. |
| `test_dcom_pack.py` | `req-dcom-pack-1..4` after import; `req-dcom-naming-1..3` via Gryphon; the two dictionary queries in `req-dcom-queries`. |

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-record-1 | CI Record Present | Proposed | `boot/ci.boot.json` exists inside the package, is named `ci`, installs only this plugin, and seeds the pack. | |
| req-dcom-record-2 | Tests Ship In The Wheel | Proposed | The tests above are inside `tap_plugin/dcom/tests/` and pass against the `ci` record. | |

### Mandatory Stamping
----
RID: `req-dcom-mandatory`

Status: `Backlog`

v0 is permissive on purpose: no manifest entry declares which dimensions a plugin's types must carry, and
no build or boot step refuses an unstamped type. The shape of that entry should be dialled in after the
rules have been used, not before.

The likely shape: a manifest surface naming the dimension keys every type in the plugin must carry,
consumed when the plugin is validated (`validate_plugin --strict`) so an unstamped type fails at author
time unless the plugin's spec states an exemption. Stamping already exists as default dimensions on every
type; "mandatory" is a check, not a mechanism. Enter a sprint only after two plugins have inherited dcom
and the omissions are visible.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-mandatory-1 | Shape Chosen After Use | Backlog | The manifest surface is specified only after two inheriting plugins have shipped. | |

### Conformance As A Report
----
RID: `req-dcom-conformance`

Status: `Backlog`

Whether a plugin that declares dcom has in fact stamped every type is readable today (`req-dcom-queries`,
last row) and computed nowhere. The report: per plugin, per type, one of three states — stamped / exempt
with a stated reason / omitted — derived from the registry and the plugin's spec, never declared by hand.
The dcom section an inheriting plugin writes under `req-dcom-inheritance` is the interim, authored form of
this report.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-conformance-1 | Three States Per Type | Backlog | The report distinguishes stamped, exempt-with-reason and omitted for every type of every inheriting plugin. | |

### Design On The Grid
----
RID: `req-dcom-design`

Status: `Backlog`

Nothing on the grid carries `design` yet. The value is defined so the model is whole and so the first
design-side plugin has a place to stand: requirements and architecture as `design` nodes, joined to the
configuration that encodes them, so "does the configuration still match the design?" becomes a query.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-dcom-design-1 | First Design Node | Backlog | A plugin ships a type stamped `dcom: design` with an edge to the configuration that encodes it. | |

### v0 Non-Goals
----
RID: `req-dcom-nongoals`

Status: `Proposed`

- **Edges between dimension nodes.** Redundant with `req-dcom-naming`; not shipped.
- **Deeper hierarchy.** One level, model and value, is all v0 defines.
- **A `design` collector.** See `req-dcom-design`.
- **Defining dcom in core.** Core owns the `dimension` type and the dimensions column; the dcom vocabulary
  is this plugin's from the first commit.

## Reference data

| Document | Contents | Seeded by |
| --- | --- | --- |
| `grift/dimensions.grift.json` | The four dimension nodes with their descriptions (`req-dcom-pack`) | Every record |

This plugin declares no `[models]` and no `[edges]`; the manifest is the source for that, and the four nodes
it seeds are instances of core's `dimension` type (`req-dcom-pack-2`).
