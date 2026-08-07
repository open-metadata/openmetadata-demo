"""Create a test suite and test case through public data-quality facades."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from typing import Any

from metadata.generated.schema.api.tests.createTestCase import CreateTestCaseRequest
from metadata.generated.schema.api.tests.createTestSuite import CreateTestSuiteRequest
from metadata.generated.schema.tests.testCase import TestCaseParameterValue
from metadata.generated.schema.type.basic import Markdown
from metadata.ingestion.ometa.utils import model_str
from metadata.sdk import (
    Tables,
    TestCases,
    TestDefinitions,
    TestSuites,
    configure,
    reset,
)

NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,31}$")
SCENARIO = "data-quality"
SUPPORTED_DEFINITION = "tableRowCountToEqual"
TEST_CASE_REQUIRED_FIELDS = ("testDefinition", "testSuite")
REQUIRED_ENV = (
    "OPENMETADATA_HOST",
    "OPENMETADATA_JWT_TOKEN",
    "OPENMETADATA_DEMO_NAMESPACE",
    "OPENMETADATA_TEST_TABLE_FQN",
    "OPENMETADATA_TEST_DEFINITION_FQN",
)


def ownership_marker(namespace: str) -> str:
    return f"[openmetadata-demo:{namespace}:{SCENARIO}]"


def validate_environment(
    environ: Mapping[str, str] | None = None,
) -> tuple[str, str, str]:
    values = os.environ if environ is None else environ
    missing = [name for name in REQUIRED_ENV if not values.get(name)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    namespace = values["OPENMETADATA_DEMO_NAMESPACE"]
    if not NAMESPACE_PATTERN.fullmatch(namespace):
        raise ValueError("OPENMETADATA_DEMO_NAMESPACE must match ^[a-z][a-z0-9_]{2,31}$")
    return (
        namespace,
        values["OPENMETADATA_TEST_TABLE_FQN"],
        values["OPENMETADATA_TEST_DEFINITION_FQN"],
    )


def table_entity_link(table_fqn: str) -> str:
    """Return OpenMetadata's canonical link for a table."""
    return f"<#E::table::{table_fqn}>"


def owned_upsert(
    facade: Any,
    fqn: str,
    request: Any,
    marker: str,
    fields: Sequence[str] | None = None,
) -> Any:
    """PUT an absent or exactly owned test entity; refuse foreign collisions."""
    existing = facade.retrieve_by_name(fqn, fields=fields, nullable=True)
    description = model_str(getattr(existing, "description", "")) if existing else ""
    if existing is not None and marker not in description:
        raise RuntimeError(f"Refusing to overwrite foreign entity: {fqn}")
    return facade.create(request)


def build_requests(
    namespace: str,
    table_fqn: str,
    definition_fqn: str,
) -> dict[str, Any]:
    """Build the suite and table-row-count case before mutation."""
    marker = ownership_marker(namespace)
    return {
        "suite": CreateTestSuiteRequest(
            name=f"{namespace}_quality_suite",
            description=Markdown(root=f"{marker} Demo data-quality suite."),
        ),
        "case": CreateTestCaseRequest(
            name=f"{namespace}_row_count_is_zero",
            description=Markdown(root=f"{marker} Demo row-count assertion."),
            testDefinition=definition_fqn,
            entityLink=table_entity_link(table_fqn),
            parameterValues=[TestCaseParameterValue(name="value", value="0")],
        ),
    }


def run_scenario(table_fqn: str, definition_fqn: str, namespace: str) -> None:
    """Preflight parents, create owned tests, and read their latest results."""
    table = Tables.retrieve_by_name(table_fqn, nullable=True)
    if table is None:
        raise RuntimeError(f"table not found: {table_fqn}")
    definition = TestDefinitions.retrieve_by_name(definition_fqn, nullable=True)
    if definition is None:
        raise RuntimeError(f"test definition not found: {definition_fqn}")
    if model_str(definition.fullyQualifiedName) != SUPPORTED_DEFINITION:
        raise RuntimeError(f"this scenario requires the built-in {SUPPORTED_DEFINITION} definition")

    requests = build_requests(namespace, table_fqn, definition_fqn)
    marker = ownership_marker(namespace)
    suite_fqn = f"{namespace}_quality_suite"
    case_fqn = f"{table_fqn}.{namespace}_row_count_is_zero"
    suite = owned_upsert(TestSuites, suite_fqn, requests["suite"], marker)
    test_case = owned_upsert(
        TestCases,
        case_fqn,
        requests["case"],
        marker,
        fields=TEST_CASE_REQUIRED_FIELDS,
    )

    result_fields = [*TEST_CASE_REQUIRED_FIELDS, "testCaseResult"]
    TestCases.retrieve_by_name(case_fqn, fields=result_fields)
    TestCases.list(
        limit=10,
        fields=result_fields,
        filters={"entityLink": table_entity_link(table_fqn)},
    )
    for entity in (suite, test_case):
        print(f"ready fqn={model_str(entity.fullyQualifiedName)} id={model_str(entity.id)}")


def main() -> int:
    try:
        namespace, table_fqn, definition_fqn = validate_environment()
        configure()
        try:
            run_scenario(table_fqn, definition_fqn, namespace)
        finally:
            reset()
    except (ValueError, RuntimeError) as exc:
        print(f"data-quality scenario failed: {exc}")
        return 1
    except Exception as exc:
        print(f"data-quality scenario failed: {type(exc).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
