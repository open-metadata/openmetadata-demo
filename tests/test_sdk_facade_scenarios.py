"""Behavior contracts for the plain OpenMetadata SDK facade scenarios."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from metadata.generated.schema.type.entityReference import EntityReference

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


def test_storage_builds_valid_rc1_requests() -> None:
    storage = load_scenario("storage-assets/storage_assets.py", "storage_assets")

    requests = storage.build_requests("demo")

    assert requests["service"].serviceType.value == "CustomStorage"
    assert requests["root"].service.root == "demo_storage_service"
    assert requests["child"].name.root == "demo_daily_exports"
    assert requests["child"].parent is None


def test_storage_sets_parent_after_both_containers_exist(monkeypatch) -> None:
    storage = load_scenario("storage-assets/storage_assets.py", "storage_assets_order")
    calls: list[str] = []

    def fake_upsert(facade, fqn, _request, _marker):
        calls.append(f"{facade.__name__}:{fqn}")
        return SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name=fqn.rsplit(".", 1)[-1],
            entityType="container",
            fullyQualifiedName=fqn,
        )

    monkeypatch.setattr(storage, "owned_upsert", fake_upsert)
    monkeypatch.setattr(
        storage.Containers,
        "retrieve_by_name",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        storage.Containers,
        "set_parent",
        lambda *_: calls.append("set_parent"),
    )
    monkeypatch.setattr(
        storage.Containers,
        "list_children",
        lambda *_args, **_kwargs: calls.append("list_children") or [],
    )
    monkeypatch.setattr(
        storage.Containers,
        "list_ancestors",
        lambda *_: calls.append("list_ancestors") or [],
    )

    storage.run_scenario("demo")

    assert calls == [
        "StorageServices:demo_storage_service",
        "Containers:demo_storage_service.demo_exports",
        "Containers:demo_storage_service.demo_daily_exports",
        "set_parent",
        "list_children",
        "list_ancestors",
    ]


TABLE_REFERENCE = EntityReference(
    id="11111111-1111-1111-1111-111111111111",
    type="table",
    name="customers",
    fullyQualifiedName="sample.database.schema.customers",
)


def test_governance_builds_valid_rc1_requests() -> None:
    governance = load_scenario("governance-assets/governance_assets.py", "governance_assets")

    requests = governance.build_requests("demo", TABLE_REFERENCE)

    assert requests["tag"].classification.root == "demo_classification"
    assert requests["term_one"].glossary.root == "demo_glossary"
    assert requests["data_product"].domains[0].root == "demo_domain"
    assert requests["data_product"].name.root == "demo_customer_product"
    assert requests["metric_one"].metricType.value == "COUNT"
    assert requests["contract"].entity.type == "table"


def test_governance_refuses_foreign_contract_before_create(monkeypatch) -> None:
    governance = load_scenario(
        "governance-assets/governance_assets.py", "governance_assets_collision"
    )
    table = SimpleNamespace(
        id="11111111-1111-1111-1111-111111111111",
        name="customers",
        entityType="table",
        fullyQualifiedName="sample.database.schema.customers",
    )
    monkeypatch.setattr(governance.Tables, "retrieve_by_name", lambda *_args, **_kwargs: table)
    monkeypatch.setattr(
        governance.DataContracts,
        "get_by_entity",
        lambda *_: SimpleNamespace(description="Created elsewhere"),
    )
    monkeypatch.setattr(
        governance,
        "owned_upsert",
        lambda *_: (_ for _ in ()).throw(AssertionError("must not mutate")),
    )

    with pytest.raises(RuntimeError, match="foreign data contract"):
        governance.run_scenario("demo", "sample.database.schema.customers")


def test_governance_orders_entities_before_relationships(monkeypatch) -> None:
    governance = load_scenario("governance-assets/governance_assets.py", "governance_assets_order")
    calls: list[str] = []
    table = SimpleNamespace(
        id="11111111-1111-1111-1111-111111111111",
        name="customers",
        entityType="table",
        fullyQualifiedName="sample.database.schema.customers",
    )

    def fake_upsert(facade, fqn, _request, _marker):
        calls.append(facade.__name__)
        return SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name=fqn.rsplit(".", 1)[-1],
            entityType=facade.__name__.lower(),
            fullyQualifiedName=fqn,
            description=governance.ownership_marker("demo"),
        )

    monkeypatch.setattr(governance.Tables, "retrieve_by_name", lambda *_args, **_kwargs: table)
    monkeypatch.setattr(governance, "owned_upsert", fake_upsert)
    monkeypatch.setattr(
        governance.GlossaryTerms,
        "add_relation",
        lambda *_args, **_kwargs: calls.append("add_relation"),
    )
    monkeypatch.setattr(
        governance.GlossaryTerms,
        "relations_graph",
        lambda *_args, **_kwargs: calls.append("relations_graph") or {},
    )
    monkeypatch.setattr(
        governance.Metrics,
        "add_related_metrics",
        lambda *_: calls.append("add_related_metrics"),
    )
    monkeypatch.setattr(
        governance.DataProducts,
        "add_assets",
        lambda *_: calls.append("add_assets") or {},
    )
    monkeypatch.setattr(
        governance.DataContracts,
        "validate_request",
        lambda *_: calls.append("validate_request"),
    )
    monkeypatch.setattr(governance.DataContracts, "get_by_entity", lambda *_: None)

    class Export:
        def as_yaml(self):
            return self

        def execute(self):
            calls.append("export_odcs")

    monkeypatch.setattr(
        governance.DataContracts,
        "export_odcs",
        lambda *_: Export(),
    )

    governance.run_scenario("demo", "sample.database.schema.customers")

    assert calls == [
        "Classifications",
        "Tags",
        "Glossaries",
        "GlossaryTerms",
        "GlossaryTerms",
        "add_relation",
        "relations_graph",
        "Domains",
        "DataProducts",
        "Metrics",
        "Metrics",
        "add_related_metrics",
        "add_assets",
        "validate_request",
        "DataContracts",
        "export_odcs",
    ]


def test_identity_builds_valid_rc1_requests() -> None:
    identity = load_scenario(
        "identity-and-settings/identity_and_settings.py", "identity_and_settings"
    )

    requests = identity.build_requests("demo", "demo.user@example.com")

    assert requests["team"].teamType.value == "Group"
    assert requests["user"].email.root == "demo.user@example.com"
    assert requests["user"].isAdmin is False
    assert requests["user"].password is None


def test_identity_reads_settings_without_mutating_them(monkeypatch) -> None:
    identity = load_scenario(
        "identity-and-settings/identity_and_settings.py",
        "identity_and_settings_order",
    )
    calls: list[str] = []

    def fake_upsert(facade, fqn, _request, _marker):
        calls.append(facade.__name__)
        return SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            name=fqn,
            entityType=facade.__name__.lower(),
            fullyQualifiedName=fqn,
        )

    monkeypatch.setattr(identity, "owned_upsert", fake_upsert)
    monkeypatch.setattr(
        identity.Settings,
        "glossary_relation_settings",
        lambda: calls.append("glossary_relation_settings") or {},
    )
    monkeypatch.setattr(
        identity.Settings,
        "glossary_relation_types",
        lambda: calls.append("glossary_relation_types") or [],
    )
    monkeypatch.setattr(
        identity.Settings,
        "define_glossary_relation_type",
        lambda *_: (_ for _ in ()).throw(AssertionError("settings must be read-only")),
    )

    identity.run_scenario("demo", "demo.user@example.com")

    assert calls == [
        "Teams",
        "Users",
        "glossary_relation_settings",
        "glossary_relation_types",
    ]
