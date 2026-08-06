"""Behavior contracts for the plain OpenMetadata SDK facade scenarios."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

ROOT = Path(__file__).parents[1]


def load_scenario(relative_path: str, module_name: str) -> ModuleType:
    """Load a standalone scenario without turning it into a package."""
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load scenario: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_builds_valid_rc1_requests() -> None:
    catalog = load_scenario("catalog-assets/catalog_assets.py", "catalog_assets")

    requests = catalog.build_requests("demo")

    assert requests["service"].serviceType.value == "CustomDatabase"
    assert requests["database"].service.root == "demo_database_service"
    assert requests["schema"].database.root == "demo_database_service.demo_database"
    assert len(requests["table"].columns) == 3
    assert requests["procedure"].databaseSchema.root.endswith(".demo_schema")


def test_owned_upsert_refuses_foreign_entity() -> None:
    catalog = load_scenario("catalog-assets/catalog_assets.py", "catalog_assets_collision")

    class Facade:
        @classmethod
        def retrieve_by_name(cls, *_args, **_kwargs):
            return SimpleNamespace(description="Created elsewhere")

        @classmethod
        def create(cls, _request):
            raise AssertionError("foreign entity must not be overwritten")

    with pytest.raises(RuntimeError, match="Refusing to overwrite"):
        catalog.owned_upsert(
            Facade,
            "demo_database_service",
            SimpleNamespace(),
            catalog.ownership_marker("demo"),
        )


def test_catalog_creates_parents_before_assets(monkeypatch) -> None:
    catalog = load_scenario("catalog-assets/catalog_assets.py", "catalog_assets_order")
    calls: list[str] = []

    def fake_upsert(facade, _fqn, _request, _marker):
        calls.append(facade.__name__)
        return SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            description="owned",
            fullyQualifiedName="demo",
            model_copy=lambda **_: SimpleNamespace(
                id="11111111-1111-1111-1111-111111111111",
                description="owned",
            ),
        )

    monkeypatch.setattr(catalog, "owned_upsert", fake_upsert)
    monkeypatch.setattr(catalog.Tables, "update", lambda entity: entity)
    monkeypatch.setattr(catalog.Tables, "add_sample_data", lambda *_: None)
    monkeypatch.setattr(catalog.Tables, "get_sample_data", lambda *_: None)

    catalog.run_scenario("demo")

    assert calls == [
        "DatabaseServices",
        "Databases",
        "DatabaseSchemas",
        "Tables",
        "StoredProcedures",
    ]


ANALYTICS_PARENTS = {
    "database_service": "sample_database_service",
    "ml_model_service": "sample_ml_service",
    "pipeline_service": "sample_pipeline_service",
    "search_service": "sample_search_service",
}


def test_analytics_builds_valid_rc1_requests() -> None:
    analytics = load_scenario("analytics-assets/analytics_assets.py", "analytics_assets")

    requests = analytics.build_requests("demo", ANALYTICS_PARENTS)

    assert requests["service"].serviceType.value == "CustomDashboard"
    assert requests["data_model"].columns[0].dataType.value == "BIGINT"
    assert requests["dashboard"].charts[0].root.endswith(".demo_chart")
    assert requests["ml_model"].mlFeatures[0].name.root == "customer_age"
    assert requests["pipeline"].tasks[0].name == "extract"
    assert requests["query"].service.root == "sample_database_service"
    assert requests["search_index"].fields[0].dataType.value == "TEXT"


def test_analytics_validates_all_parent_environment() -> None:
    analytics = load_scenario(
        "analytics-assets/analytics_assets.py", "analytics_assets_environment"
    )
    environment = {
        "OPENMETADATA_HOST": "http://localhost:8585/api",
        "OPENMETADATA_JWT_TOKEN": "not-a-real-token",
        "OPENMETADATA_DEMO_NAMESPACE": "demo",
    }

    with pytest.raises(ValueError, match="OPENMETADATA_DATABASE_SERVICE_FQN"):
        analytics.validate_environment(environment)


def test_analytics_orders_assets_and_pipeline_status(monkeypatch) -> None:
    analytics = load_scenario("analytics-assets/analytics_assets.py", "analytics_assets_order")
    calls: list[str] = []

    def fake_upsert(facade, _fqn, _request, _marker):
        calls.append(facade.__name__)
        return SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            fullyQualifiedName="demo",
        )

    monkeypatch.setattr(analytics, "owned_upsert", fake_upsert)
    monkeypatch.setattr(
        analytics.Pipelines,
        "add_pipeline_status",
        lambda *_: calls.append("add_pipeline_status"),
    )
    monkeypatch.setattr(
        analytics.Pipelines,
        "list_pipeline_statuses",
        lambda *_args, **_kwargs: calls.append("list_pipeline_statuses") or [],
    )

    analytics.run_scenario("demo", ANALYTICS_PARENTS)

    assert calls == [
        "DashboardServices",
        "Charts",
        "DashboardDataModels",
        "Dashboards",
        "MLModels",
        "Pipelines",
        "add_pipeline_status",
        "list_pipeline_statuses",
        "Queries",
        "SearchIndexes",
    ]
