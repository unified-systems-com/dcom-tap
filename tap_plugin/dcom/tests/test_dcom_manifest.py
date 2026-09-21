"""Structural, strict and loads validation for the dcom plugin, plus the identity chain.

`req-dcom-record`. dcom is a vocabulary plugin: the whole of what it ships is four
dimension nodes in one GRIFT bundle, so what there is to validate structurally is the
identity chain, the absence of every surface it deliberately does not have, and the `ci`
boot record that makes its own tests runnable by CI.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from tap.plugin_testing import find_plugin_source_root
from tap_plugins.manifest import load_manifest
from tap_plugins.validate.service import validate_plugin

PLUGIN_ROOT = find_plugin_source_root(__file__)
PACKAGE_ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    PLUGIN_ROOT is None,
    reason="source-layout validation needs the plugin source tree; installed as a wheel here "
    "(delegated to the plugin repo's own build).",
)


class TestValidation:
    """The validator is the authority on structure; do not re-implement its checks here."""

    def test_structure_passes(self) -> None:
        result = validate_plugin(PLUGIN_ROOT, level="structure")
        assert result.ok, result.to_human()

    def test_strict_passes(self) -> None:
        result = validate_plugin(PLUGIN_ROOT, level="structure", strict=True)
        assert result.ok, result.to_human()

    def test_loads_passes(self) -> None:
        result = validate_plugin(PLUGIN_ROOT, level="loads", strict=True)
        assert result.ok, result.to_human()


class TestIdentityChain:
    """slug == dist == namespace == entry-point key (`req-tap-plugin-arch-identity`).

    The validator checks the chain agrees; these assert the VALUES, so a rename that
    kept the chain internally consistent still has to be a deliberate edit here.
    """

    @staticmethod
    def _pyproject() -> dict:
        assert PLUGIN_ROOT is not None
        with (PLUGIN_ROOT / "pyproject.toml").open("rb") as fh:
            return tomllib.load(fh)

    def test_dist_name(self) -> None:
        from tap.plugin_identity import dist_name_for_slug

        assert self._pyproject()["project"]["name"] == dist_name_for_slug("dcom") == "dcom-tap"

    def test_entry_point(self) -> None:
        entry_points = self._pyproject()["project"]["entry-points"]["tap.plugins"]
        assert entry_points == {"dcom": "tap_plugin.dcom.apps:DcomConfig"}

    def test_namespace_has_no_init(self) -> None:
        assert PLUGIN_ROOT is not None
        # PEP 420: tap_plugin/ is a namespace package shared by every plugin dist.
        assert not (PLUGIN_ROOT / "tap_plugin" / "__init__.py").exists()

    def test_manifest_slug(self) -> None:
        assert load_manifest(PACKAGE_ROOT).slug == "dcom"


class TestSurfaces:
    """What dcom deliberately does NOT ship. Absence here is a decision, not an omission."""

    @staticmethod
    def _raw_manifest() -> dict:
        with (PACKAGE_ROOT / "tap-plugin.toml").open("rb") as fh:
            return tomllib.load(fh)

    def test_no_models_no_edges(self) -> None:
        manifest = load_manifest(PACKAGE_ROOT)
        assert manifest.models == []
        assert manifest.edges == []

    def test_exactly_one_grift_bundle(self) -> None:
        grift = load_manifest(PACKAGE_ROOT).grift
        assert [entry.path for entry in grift] == ["grift/dimensions.grift.json"]

    def test_no_dependencies(self) -> None:
        """Core's `dimension` model is the only type dcom writes; every dependency
        direction is INTO this plugin (spec-dcom-v0.md, Plugin Identity)."""
        assert self._raw_manifest().get("depends_on", []) == []
        assert self._pyproject_dependencies() == []

    @staticmethod
    def _pyproject_dependencies() -> list[str]:
        assert PLUGIN_ROOT is not None
        with (PLUGIN_ROOT / "pyproject.toml").open("rb") as fh:
            return tomllib.load(fh)["project"]["dependencies"]

    def test_fips_posture_declared(self) -> None:
        """Declare-vs-decide (`spec-fips.md`): absent is undeclared, not compatible."""
        assert self._raw_manifest()["fips"]["status"] == "compatible"


class TestCiRecord:
    """`req-dcom-record-1` / `req-boot-bootstrap-ci-record`. The validator checks the
    record's digest, closure, credential-freedom and abort-on-failure; what is asserted
    here is the two facts specific to dcom: it installs ITSELF ALONE, and it seeds the pack."""

    @staticmethod
    def _record() -> dict:
        import json

        return json.loads((PACKAGE_ROOT / "boot" / "ci.boot.json").read_text(encoding="utf-8"))

    def test_installs_only_itself(self) -> None:
        installed = [entry["slug"] for entry in self._record()["install"]["plugins"]]
        assert installed == ["dcom"]

    def test_seeds_its_own_pack(self) -> None:
        steps = self._record()["population"]["steps"]
        assert [(step["type"], step["plugin"]) for step in steps] == [("seed-plugin", "dcom")]

    def test_declared_in_the_manifest(self) -> None:
        records = {entry["name"] for entry in self._raw_boot_records()}
        assert "ci" in records

    @staticmethod
    def _raw_boot_records() -> list[dict]:
        with (PACKAGE_ROOT / "tap-plugin.toml").open("rb") as fh:
            return tomllib.load(fh)["boot"]["records"]
