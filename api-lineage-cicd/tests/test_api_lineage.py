"""Tests for the declarative API lineage example."""

from types import SimpleNamespace

import pytest
from api_lineage_cicd import (
    APICollections,
    APIEndpoints,
    Lineage,
    apply_api_assets,
    build_api_assets,
    build_api_collection_request,
    build_api_endpoint_request,
    build_api_schema,
    build_column_lineage,
    create_lineage,
    load_yaml,
    ownership_marker,
    validate_environment,
    verify_lineage,
)
from metadata.generated.schema.type.entityLineage import Edge


def test_environment_validation_respects_an_explicit_empty_mapping(monkeypatch) -> None:
    """Tests should not fall back to process credentials when a mapping is supplied."""
    monkeypatch.setenv("OPENMETADATA_HOST", "https://metadata.example.com/api")
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")

    with pytest.raises(RuntimeError, match="OPENMETADATA_HOST"):
        validate_environment({})


def test_environment_requires_namespace_and_existing_services() -> None:
    with pytest.raises(RuntimeError, match="OPENMETADATA_DEMO_NAMESPACE"):
        validate_environment(
            {
                "OPENMETADATA_HOST": "https://metadata.example.com/api",
                "OPENMETADATA_JWT_TOKEN": "test-token",
            }
        )


def test_api_yaml_builds_valid_2_0_schema_models() -> None:
    """Every endpoint schema in the checked-in YAML should validate."""
    orders = load_yaml("orders_api.yaml")

    schemas = [
        build_api_schema(endpoint.get(schema_name))
        for collection in orders["collections"]
        for endpoint in collection["endpoints"]
        for schema_name in ("requestSchema", "responseSchema")
        if endpoint.get(schema_name)
    ]

    assert len(schemas) == 3
    assert all(schema.schemaType.value == "JSON" for schema in schemas)


def test_api_yaml_builds_valid_2_0_create_requests() -> None:
    """Declarative collection and endpoint inputs must all validate."""
    request_counts = {}
    for filename in ("orders_api.yaml", "fulfillment_api.yaml"):
        raw = load_yaml(filename)
        requests = []
        for collection in raw["collections"]:
            collection_fqn = f"{raw['serviceName']}.{collection['name']}"
            requests.append(
                build_api_collection_request(
                    collection,
                    raw["serviceName"],
                    ownership_marker("demo"),
                )
            )
            requests.extend(
                build_api_endpoint_request(
                    endpoint,
                    collection_fqn,
                    ownership_marker("demo"),
                )
                for endpoint in collection["endpoints"]
            )
        request_counts[filename] = len(requests)

    assert request_counts == {"orders_api.yaml": 3, "fulfillment_api.yaml": 3}


def test_api_assets_use_supplied_parent_and_marker() -> None:
    assets = build_api_assets(
        load_yaml("orders_api.yaml"),
        "existing-orders-service",
        ownership_marker("demo"),
    )

    assert assets[0][0] is APICollections
    assert assets[0][1] == "existing-orders-service.orders"
    assert assets[0][2].service.root == "existing-orders-service"
    assert ownership_marker("demo") in assets[0][2].description.root
    assert assets[1][0] is APIEndpoints
    assert assets[1][1].startswith("existing-orders-service.orders.")


def test_api_assets_refuse_foreign_collisions(monkeypatch) -> None:
    assets = build_api_assets(
        load_yaml("orders_api.yaml"),
        "existing-orders-service",
        ownership_marker("demo"),
    )
    monkeypatch.setattr(
        APICollections,
        "retrieve_by_name",
        lambda *_args, **_kwargs: SimpleNamespace(description="Created elsewhere"),
    )

    with pytest.raises(RuntimeError, match="Refusing to overwrite"):
        apply_api_assets(assets, ownership_marker("demo"))


def test_missing_parent_service_has_a_clear_error(monkeypatch) -> None:
    assets = build_api_assets(
        load_yaml("orders_api.yaml"),
        "missing-orders-service",
        ownership_marker("demo"),
    )
    monkeypatch.setattr(APICollections, "retrieve_by_name", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        APICollections,
        "create",
        lambda *_: (_ for _ in ()).throw(LookupError("not found")),
    )

    with pytest.raises(RuntimeError, match="missing-orders-service"):
        apply_api_assets(assets, ownership_marker("demo"))


def test_lineage_replaces_logical_service_names_with_supplied_fqns() -> None:
    mappings = {
        "orders-api": "existing-orders-service",
        "fulfillment-api": "existing-fulfillment-service",
    }
    edge = load_yaml("lineage.yaml")["edges"][0]

    columns = build_column_lineage(edge["columnLineage"], mappings)

    assert columns is not None
    assert columns[0].fromColumns[0].root.startswith("existing-orders-service.")
    assert columns[0].toColumn.root.startswith("existing-fulfillment-service.")


def test_lineage_yaml_builds_column_lineage_models() -> None:
    """The declarative mappings should remain valid generated 2.0 models."""
    lineage = load_yaml("lineage.yaml")

    columns = build_column_lineage(lineage["edges"][0]["columnLineage"])

    assert columns is not None
    assert len(columns) == 3
    assert columns[0].function.root == "IDENTITY()"


def test_lineage_edges_reference_fields_declared_by_their_endpoints() -> None:
    """Every opaque lineage FQN should still describe a possible data flow."""
    services = {
        raw["serviceName"]: raw
        for raw in (load_yaml("orders_api.yaml"), load_yaml("fulfillment_api.yaml"))
    }

    def schema_field_paths(fields: list[dict], prefix: str = "") -> set[str]:
        paths = set()
        for field in fields:
            path = f"{prefix}.{field['name']}" if prefix else field["name"]
            paths.add(path)
            paths.update(schema_field_paths(field.get("children", []), path))
        return paths

    def assert_declared(column_fqn: str) -> None:
        service_name, collection_name, endpoint_name, schema_name, field_path = column_fqn.split(
            ".", maxsplit=4
        )
        service = services[service_name]
        collection = next(
            item for item in service["collections"] if item["name"] == collection_name
        )
        endpoint = next(item for item in collection["endpoints"] if item["name"] == endpoint_name)
        fields = schema_field_paths(endpoint[schema_name]["schemaFields"])
        assert field_path in fields, column_fqn

    for edge in load_yaml("lineage.yaml")["edges"]:
        for mapping in edge["columnLineage"]:
            for source_column in mapping["fromColumns"]:
                assert_declared(source_column)
            assert_declared(mapping["toColumn"])


def test_lineage_registration_builds_requests_behind_mocked_sdk_boundaries(
    monkeypatch,
    capsys,
) -> None:
    """The example should construct lineage without requiring a test server."""
    created = []
    entity = SimpleNamespace(id="11111111-1111-1111-1111-111111111111")
    monkeypatch.setattr(APIEndpoints, "retrieve_by_name", lambda _fqn: entity)
    monkeypatch.setattr(Lineage, "add_lineage_request", created.append)
    raw = load_yaml("lineage.yaml")

    create_lineage(raw)

    assert len(created) == 2
    assert created[0].edge.fromEntity.type == "apiEndpoint"
    assert created[0].edge.toEntity.type == "apiEndpoint"
    assert len(created[0].edge.lineageDetails.columnsLineage) == 3
    assert len(created[1].edge.lineageDetails.columnsLineage) == 2
    output = capsys.readouterr().out
    assert "root=" not in output
    assert "orders-api.orders.createOrder.responseSchema.order_id --[IDENTITY()]-->" in output


def test_lineage_verification_uses_mocked_sdk_boundaries(monkeypatch, capsys) -> None:
    """Verification should require every requested edge without contacting a server."""
    ids = {
        "orders-api.orders.createOrder": "11111111-1111-1111-1111-111111111111",
        "fulfillment-api.shipments.createShipment": "22222222-2222-2222-2222-222222222222",
        "orders-api.orders.getOrder": "33333333-3333-3333-3333-333333333333",
        "fulfillment-api.shipments.getShipment": "44444444-4444-4444-4444-444444444444",
    }
    calls = []
    source_by_target = {
        ids["fulfillment-api.shipments.createShipment"]: ids["orders-api.orders.createOrder"],
        ids["fulfillment-api.shipments.getShipment"]: ids["orders-api.orders.getOrder"],
    }
    monkeypatch.setattr(
        APIEndpoints,
        "retrieve_by_name",
        lambda fqn: SimpleNamespace(id=ids[fqn]),
    )

    def fake_get_entity_lineage(**kwargs):
        calls.append(kwargs)
        to_id = str(kwargs["entity_id"])
        from_id = source_by_target[to_id]
        return SimpleNamespace(
            upstreamEdges=[Edge(fromEntity=from_id, toEntity=to_id)],
            downstreamEdges=[],
        )

    monkeypatch.setattr(Lineage, "get_entity_lineage", fake_get_entity_lineage)

    verify_lineage(load_yaml("lineage.yaml"))

    assert len(calls) == 2
    assert all(call["upstream_depth"] == 1 for call in calls)
    assert all(call["downstream_depth"] == 1 for call in calls)
    assert "Verified 2 lineage edges" in capsys.readouterr().out


def test_lineage_verification_fails_when_a_requested_edge_is_missing(monkeypatch) -> None:
    """A zero-edge response must make the CI/CD command fail."""
    ids = {
        "orders-api.orders.createOrder": "11111111-1111-1111-1111-111111111111",
        "fulfillment-api.shipments.createShipment": "22222222-2222-2222-2222-222222222222",
        "orders-api.orders.getOrder": "33333333-3333-3333-3333-333333333333",
        "fulfillment-api.shipments.getShipment": "44444444-4444-4444-4444-444444444444",
    }
    monkeypatch.setattr(
        APIEndpoints,
        "retrieve_by_name",
        lambda fqn: SimpleNamespace(id=ids[fqn]),
    )
    monkeypatch.setattr(
        Lineage,
        "get_entity_lineage",
        lambda **_: SimpleNamespace(upstreamEdges=[], downstreamEdges=[]),
    )

    with pytest.raises(RuntimeError, match="Missing lineage edge"):
        verify_lineage(load_yaml("lineage.yaml"))
