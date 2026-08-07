"""AST and import-safety contracts for the lean SDK facade catalog."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import metadata.sdk as sdk
from metadata.ingestion.ometa.ometa_api import (
    MissingEntityTypeException,
    OpenMetadata,
)
from metadata.sdk.entities import __all__ as SDK_FACADES

ROOT = Path(__file__).parents[1]
BROKEN_RC1_FACADES = {"ContextFiles", "Folders", "Pages"}
SETTINGS_FACADE = "Settings"
FACADE_SCRIPTS = (
    ROOT / "catalog-assets/catalog_assets.py",
    ROOT / "analytics-assets/analytics_assets.py",
    ROOT / "storage-assets/storage_assets.py",
    ROOT / "governance-assets/governance_assets.py",
    ROOT / "identity-and-settings/identity_and_settings.py",
    ROOT / "data-quality/data_quality.py",
    ROOT / "api-lineage-cicd/api_lineage_cicd.py",
    ROOT / "dynamic_csv_importer/csv_importer.py",
)


def executable_facade_calls(path: Path, facades: set[str]) -> set[str]:
    """Find facade method calls and facade arguments to the local upsert helper."""
    tree = ast.parse(path.read_text(), filename=str(path))
    called: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in facades
            and node.func.attr not in {"entity_type", "to_entity_reference"}
        ):
            called.add(node.func.value.id)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "owned_upsert"
            and node.args
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id in facades
        ):
            called.add(node.args[0].id)
    return called


def direct_methods(path: Path, facade: str) -> set[str]:
    """Return methods invoked directly on one facade name."""
    tree = ast.parse(path.read_text(), filename=str(path))
    return {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == facade
    }


def test_exact_rc1_route_backed_facades_are_executable() -> None:
    """Every exported facade with an RC1 route must have real executable use."""
    exported = set(SDK_FACADES)
    route_backed = exported - BROKEN_RC1_FACADES - {SETTINGS_FACADE}
    missing_routes = set()
    for name in exported - {SETTINGS_FACADE}:
        facade = getattr(sdk, name)
        try:
            OpenMetadata.get_suffix(facade.entity_type())
        except MissingEntityTypeException:
            missing_routes.add(name)

    covered = set().union(*(executable_facade_calls(path, route_backed) for path in FACADE_SCRIPTS))

    assert missing_routes == BROKEN_RC1_FACADES
    assert covered == route_backed


def test_settings_reads_and_broken_facades_are_explicit() -> None:
    """Settings is live read-only; broken Context Center facades stay documented."""
    identity_path = ROOT / "identity-and-settings/identity_and_settings.py"
    identity_calls = executable_facade_calls(identity_path, {SETTINGS_FACADE})
    settings_methods = direct_methods(identity_path, SETTINGS_FACADE)
    limitation = (ROOT / "SDK_FACADE_LIMITATIONS.md").read_text()
    scenario_tests = (ROOT / "tests/test_sdk_facade_scenarios.py").read_text()

    assert identity_calls == {SETTINGS_FACADE}
    assert settings_methods == {
        "glossary_relation_settings",
        "glossary_relation_types",
    }
    for name in BROKEN_RC1_FACADES:
        assert name in limitation
        assert name in scenario_tests


def test_facade_examples_do_not_restore_platform_or_private_clients() -> None:
    """Keep the catalog as plain examples, not a generated runtime or SDK wrapper."""
    assert not (ROOT / "platform-api").exists()
    for path in FACADE_SCRIPTS:
        source = path.read_text()
        assert "openmetadata_demo_api" not in source
        assert "client().ometa" not in source


def test_facade_script_imports_cannot_open_sockets() -> None:
    """Import every live script in a fresh process with socket events denied."""
    probe = """
import runpy
import sys

def deny_socket(event, _args):
    if event in {"socket.connect", "socket.bind"}:
        raise RuntimeError(f"network attempted during import: {event}")

sys.addaudithook(deny_socket)
for index, path in enumerate(sys.argv[1:]):
    runpy.run_path(path, run_name=f"facade_import_{index}")
"""
    result = subprocess.run(
        [sys.executable, "-c", probe, *(str(path) for path in FACADE_SCRIPTS)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_facade_scripts_configure_the_sdk_only_in_main() -> None:
    """Keep global SDK configuration out of imports and reusable helpers."""
    for path in FACADE_SCRIPTS:
        tree = ast.parse(path.read_text(), filename=str(path))
        callers = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Name)
                and call.func.id == "configure"
                for call in ast.walk(node)
            )
        }
        assert callers == {"main"}, path


def test_rc1_broken_helpers_are_not_presented_as_working() -> None:
    """Keep live examples on the public facade paths that work in exact RC1."""
    storage = ROOT / "storage-assets/storage_assets.py"
    governance = ROOT / "governance-assets/governance_assets.py"
    limitation = (ROOT / "SDK_FACADE_LIMITATIONS.md").read_text()

    assert "set_parent" not in direct_methods(storage, "Containers")
    assert "add_related_metrics" not in direct_methods(governance, "Metrics")
    assert "validate_request" not in direct_methods(governance, "DataContracts")
    for method in (
        "Containers.set_parent()",
        "Metrics.add_related_metrics()",
        "DataContracts.validate_request()",
    ):
        assert method in limitation
