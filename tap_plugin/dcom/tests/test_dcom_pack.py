"""The dimension pack, proved by importing it into a grid (`req-dcom-pack`, `req-dcom-naming`, `req-dcom-queries`).

Nothing here reads the bundle and calls that a result. The bundle is imported through
`grift_import` and every assertion is made against what came back out of the grid — the
`dimension` rows and their spine entities — because what ships is a claim about the grid,
not about a JSON file.

The one exception is `TestBundleMatchesTheSpec`, which compares the bundle's description
text to the spec's own table. That is a source-tree check (the spec does not ride in the
wheel) and it exists so the prose a Player-3 reader gets is the prose the spec promises,
with one authored copy and one derived comparison rather than two copies nobody diffs.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from tap.plugin_testing import find_plugin_source_root

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = PACKAGE_ROOT / "grift" / "dimensions.grift.json"
PLUGIN_ROOT = find_plugin_source_root(__file__)

AXIS = "dcom"
VALUES = ("design", "configuration", "operation")
VALUE_NAMES = tuple(f"{AXIS}.{value}" for value in VALUES)
ALL_NAMES = (AXIS, *VALUE_NAMES)

pytestmark = pytest.mark.django_db(databases=["default", "search_readonly"])

# A Gryphon read runs on the `search_readonly` alias — a SECOND connection to the same
# database. Inside the default transactional test case it cannot see rows the import wrote
# on `default`, so every canonical query would come back empty and read as "the pack is not
# there" rather than "the reader cannot see it yet" — absence of evidence rendered as
# evidence of absence. `transaction=True` commits, so the reader sees what a reader sees.
# Scoped to the classes that read, not the module: it flushes the database between tests.
READS_THROUGH_GRYPHON = pytest.mark.django_db(transaction=True, databases=["default", "search_readonly"])


def _bundle() -> dict:
    return json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def seeded() -> dict[str, object]:
    """Import the pack and hand back the `dimension` rows it produced, keyed by name."""
    from tap_grid.grift import grift_import
    from tap_grid.models import Dimension

    result = grift_import(_bundle())
    assert result.success, result
    return {row.name: row for row in Dimension.objects.filter(name__startswith=AXIS)}


class TestFourNodes:
    """`req-dcom-pack-1`, `-2`, `-4`."""

    def test_exactly_four_dimension_nodes(self, seeded: dict) -> None:
        assert sorted(seeded) == sorted(ALL_NAMES)

    def test_every_node_is_a_dimension(self, seeded: dict) -> None:
        from tap_grid.models import Dimension

        for name in ALL_NAMES:
            assert isinstance(seeded[name], Dimension)
            assert seeded[name].entity.entity_type == "dimension"

    def test_bundle_declares_no_edges(self, seeded: dict) -> None:
        """`req-dcom-pack-2`: the naming rule makes parent/child edges a second copy of a
        fact the name already carries. Asserted on the grid AND on the bundle, because an
        edge that failed to import would look the same as an edge that was never declared."""
        from tap_grid.models import Edge

        assert all(batch["edges"] == [] for batch in _bundle()["batches"])
        entity_ids = [row.entity_id for row in seeded.values()]
        assert not Edge.objects.filter(from_entity_id__in=entity_ids).exists()
        assert not Edge.objects.filter(to_entity_id__in=entity_ids).exists()

    def test_every_node_carries_tap_meta_dimension(self, seeded: dict) -> None:
        for name in ALL_NAMES:
            assert seeded[name].entity.dimensions["tap.meta"] == "dimension"

    def test_the_dictionary_carries_no_dcom_value(self, seeded: dict) -> None:
        """`req-dcom-pack-4`: the pack is the dictionary, and dictionary entries are not
        entries in themselves."""
        for name in ALL_NAMES:
            assert AXIS not in seeded[name].entity.dimensions, name


class TestDescriptions:
    """`req-dcom-pack-3` — properties, not a byte-match, so the prose can be improved
    without a spec edit. What must hold: each description is there, names its own value,
    and (for the three value nodes) states the mutability rule."""

    MUTABILITY = {
        "dcom.design": ("edited", "supersede"),
        "dcom.configuration": ("changes under you", "version"),
        "dcom.operation": ("immutable", "never changed"),
    }

    def test_non_empty(self, seeded: dict) -> None:
        for name in ALL_NAMES:
            assert seeded[name].description.strip(), name

    def test_each_value_node_names_its_own_value(self, seeded: dict) -> None:
        for name in VALUE_NAMES:
            value = name.split(".")[-1]
            assert value in seeded[name].description, name

    def test_the_axis_node_names_all_three_values(self, seeded: dict) -> None:
        description = seeded[AXIS].description
        for name in VALUE_NAMES:
            assert name in description

    def test_each_value_node_states_its_mutability_rule(self, seeded: dict) -> None:
        for name, phrases in self.MUTABILITY.items():
            description = seeded[name].description.lower()
            assert any(phrase in description for phrase in phrases), name


@READS_THROUGH_GRYPHON
class TestNaming:
    """`req-dcom-naming-1..3`, read through Gryphon: everything about the hierarchy is
    derived from the name, so the derivations are what is tested."""

    def test_prefix_enumerates_values(self, seeded: dict) -> None:
        from tap_grid.gryphon import execute_gryphon_raw

        envelope = execute_gryphon_raw(
            'MATCH (d:dimension) WHERE d.name STARTS_WITH "dcom." RETURN d', {}
        )
        names = sorted(node["name"] for node in envelope["nodes"])
        assert names == sorted(VALUE_NAMES)

    def test_last_segment_is_the_value_and_the_prefix_is_the_axis(self, seeded: dict) -> None:
        for name in VALUE_NAMES:
            prefix, _, last = name.rpartition(".")
            assert prefix == AXIS
            assert last in VALUES

    def test_no_dot_in_a_value(self, seeded: dict) -> None:
        for name in VALUE_NAMES:
            assert "." not in name.rpartition(".")[2], name

    def test_the_axis_has_no_parent(self, seeded: dict) -> None:
        assert "." not in AXIS


@READS_THROUGH_GRYPHON
class TestCanonicalQueries:
    """`req-dcom-queries-1` — every canonical query parses and executes against a grid with
    the pack seeded. The two DICTIONARY queries return the pack. The three CONTAINMENT
    queries are executed here to prove they run, and return nothing because dcom stamps
    nothing itself; what they return once a value is on the grid is proven by the first
    inheriting plugin."""

    def test_what_the_axis_means(self, seeded: dict) -> None:
        from tap_grid.gryphon import execute_gryphon_raw

        envelope = execute_gryphon_raw('MATCH (d:dimension) WHERE d.name = "dcom" RETURN d', {})
        assert [node["name"] for node in envelope["nodes"]] == [AXIS]

    def test_what_values_it_allows_with_their_meanings(self, seeded: dict) -> None:
        from tap_grid.gryphon import execute_gryphon_raw

        envelope = execute_gryphon_raw(
            'MATCH (d:dimension) WHERE d.name STARTS_WITH "dcom." RETURN d', {}
        )
        assert len(envelope["nodes"]) == len(VALUE_NAMES)
        for node in envelope["nodes"]:
            # "…with their meanings": the meaning rides the data lane of the full layer,
            # so a reader gets the vocabulary and its prose from this one query.
            assert node["data"]["description"].strip(), node["name"]

    @pytest.mark.parametrize("value", VALUES)
    def test_a_whole_side_of_the_grid_parses_and_executes(self, seeded: dict, value: str) -> None:
        from tap_grid.gryphon import execute_gryphon_raw

        envelope = execute_gryphon_raw(
            f'MATCH (n) WHERE n.dimensions["dcom"] = "{value}" RETURN n', {}
        )
        # Nothing on this grid carries a dcom value: the pack is the dictionary, not an
        # entry in it (`req-dcom-pack-4`). An inheriting plugin is what makes this non-empty.
        assert envelope["nodes"] == []

    def test_the_unstamped_third_state_parses_and_executes(self, seeded: dict) -> None:
        """`req-dcom-queries` last row / `req-dcom-stamping-2`: absence of the key is the
        third state, and it is readable. Here every dimension node is in it."""
        from tap_grid.gryphon import execute_gryphon_raw

        envelope = execute_gryphon_raw(
            'MATCH (n:dimension) WHERE n.dimensions["dcom"] IS NULL RETURN n', {}
        )
        found = {node["name"] for node in envelope["nodes"]}
        assert set(ALL_NAMES) <= found


class TestIdempotent:
    """Upsert, not duplicate: every boot re-runs the import (`req-tap-plugin-manifest-v0-grift-7`)."""

    def test_second_import_changes_nothing(self, seeded: dict) -> None:
        from tap_grid.grift import grift_import
        from tap_grid.models import Dimension

        before = {row.name: row.entity_id for row in Dimension.objects.filter(name__startswith=AXIS)}
        assert grift_import(_bundle()).success
        after = {row.name: row.entity_id for row in Dimension.objects.filter(name__startswith=AXIS)}
        assert after == before


@pytest.mark.skipif(
    PLUGIN_ROOT is None,
    reason="the spec does not ride in the wheel; this comparison is a source-tree check.",
)
class TestBundleMatchesTheSpec:
    """The shipped descriptions ARE the spec's table (`req-dcom-pack`, whose Implementation
    section calls the table verbatim). One authored copy, one derived comparison."""

    # `| `dcom.design` | value | The `design` position … |` — three cells, the last one prose.
    ROW = re.compile(r"^\|\s*`(dcom(?:\.\w+)?)`\s*\|\s*(axis|value)\s*\|\s*(.+?)\s*\|\s*$", re.MULTILINE)

    @classmethod
    def _spec_descriptions(cls) -> dict[str, str]:
        assert PLUGIN_ROOT is not None
        spec = (PLUGIN_ROOT / "specs" / "spec-dcom-v0.md").read_text(encoding="utf-8")
        return {name: description for name, _role, description in cls.ROW.findall(spec)}

    def test_the_spec_table_is_parseable_and_complete(self) -> None:
        # A regex that matched nothing would make every comparison below vacuously true.
        assert sorted(self._spec_descriptions()) == sorted(ALL_NAMES)

    def test_descriptions_match_verbatim(self, seeded: dict) -> None:
        spec = self._spec_descriptions()
        for name in ALL_NAMES:
            assert seeded[name].description == spec[name], name

    def test_names_match_verbatim(self, seeded: dict) -> None:
        assert sorted(self._spec_descriptions()) == sorted(seeded)
