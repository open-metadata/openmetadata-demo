"""Create related governance assets with the public OpenMetadata facades."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any

from metadata.generated.schema.api.classification.createClassification import (
    CreateClassificationRequest,
)
from metadata.generated.schema.api.classification.createTag import CreateTagRequest
from metadata.generated.schema.api.data.createDataContract import (
    CreateDataContractRequest,
)
from metadata.generated.schema.api.data.createGlossary import CreateGlossaryRequest
from metadata.generated.schema.api.data.createGlossaryTerm import (
    CreateGlossaryTermRequest,
)
from metadata.generated.schema.api.data.createMetric import CreateMetricRequest
from metadata.generated.schema.api.domains.createDataProduct import (
    CreateDataProductRequest,
)
from metadata.generated.schema.api.domains.createDomain import CreateDomainRequest
from metadata.generated.schema.entity.data.metric import (
    Language,
    MetricExpression,
    MetricType,
    UnitOfMeasurement,
)
from metadata.generated.schema.entity.domains.domain import DomainType
from metadata.generated.schema.type.basic import Markdown
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.ingestion.ometa.utils import model_str
from metadata.sdk import (
    Classifications,
    DataContracts,
    DataProducts,
    Domains,
    Glossaries,
    GlossaryTerms,
    Metrics,
    Tables,
    Tags,
    configure,
    reset,
)

NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,31}$")
SCENARIO = "governance-assets"
REQUIRED_ENV = (
    "OPENMETADATA_HOST",
    "OPENMETADATA_JWT_TOKEN",
    "OPENMETADATA_DEMO_NAMESPACE",
    "OPENMETADATA_CONTRACT_TABLE_FQN",
)


def ownership_marker(namespace: str) -> str:
    return f"[openmetadata-demo:{namespace}:{SCENARIO}]"


def validate_environment(
    environ: Mapping[str, str] | None = None,
) -> tuple[str, str]:
    values = os.environ if environ is None else environ
    missing = [name for name in REQUIRED_ENV if not values.get(name)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    namespace = values["OPENMETADATA_DEMO_NAMESPACE"]
    if not NAMESPACE_PATTERN.fullmatch(namespace):
        raise ValueError("OPENMETADATA_DEMO_NAMESPACE must match ^[a-z][a-z0-9_]{2,31}$")
    return namespace, values["OPENMETADATA_CONTRACT_TABLE_FQN"]


def owned_upsert(
    facade: Any,
    fqn: str,
    request: Any,
    marker: str,
) -> Any:
    """PUT an absent or exactly owned entity; refuse foreign collisions."""
    existing = facade.retrieve_by_name(fqn, nullable=True)
    description = model_str(getattr(existing, "description", "")) if existing else ""
    if existing is not None and marker not in description:
        raise RuntimeError(f"Refusing to overwrite foreign entity: {fqn}")
    return facade.create(request)


def build_requests(
    namespace: str,
    table_reference: EntityReference,
) -> dict[str, Any]:
    """Build all governance requests before the first mutation."""
    marker = ownership_marker(namespace)
    classification = f"{namespace}_classification"
    glossary = f"{namespace}_glossary"
    domain = f"{namespace}_domain"
    return {
        "classification": CreateClassificationRequest(
            name=classification,
            description=Markdown(root=f"{marker} Demo classification."),
        ),
        "tag": CreateTagRequest(
            name=f"{namespace}_sensitive",
            description=Markdown(root=f"{marker} Demo sensitivity tag."),
            classification=classification,
        ),
        "glossary": CreateGlossaryRequest(
            name=glossary,
            description=Markdown(root=f"{marker} Demo business glossary."),
        ),
        "term_one": CreateGlossaryTermRequest(
            name=f"{namespace}_customer",
            description=Markdown(root=f"{marker} A person buying a product."),
            glossary=glossary,
        ),
        "term_two": CreateGlossaryTermRequest(
            name=f"{namespace}_account",
            description=Markdown(root=f"{marker} A customer's commercial account."),
            glossary=glossary,
        ),
        "domain": CreateDomainRequest(
            name=domain,
            description=Markdown(root=f"{marker} Demo customer domain."),
            domainType=DomainType.Consumer_aligned,
        ),
        "data_product": CreateDataProductRequest(
            name=f"{namespace}_customer_product",
            description=Markdown(root=f"{marker} Demo customer data product."),
            domains=[domain],
        ),
        "metric_one": CreateMetricRequest(
            name=f"{namespace}_customer_count",
            description=Markdown(root=f"{marker} Number of customers."),
            metricType=MetricType.COUNT,
            unitOfMeasurement=UnitOfMeasurement.COUNT,
            metricExpression=MetricExpression(language=Language.SQL, code="COUNT(*)"),
        ),
        "metric_two": CreateMetricRequest(
            name=f"{namespace}_active_customer_rate",
            description=Markdown(root=f"{marker} Share of active customers."),
            metricType=MetricType.PERCENTAGE,
            unitOfMeasurement=UnitOfMeasurement.PERCENTAGE,
            metricExpression=MetricExpression(
                language=Language.SQL,
                code="100 * SUM(CASE WHEN is_active THEN 1 ELSE 0 END) / COUNT(*)",
            ),
        ),
        "contract": CreateDataContractRequest(
            name=f"{namespace}_customer_contract",
            description=Markdown(root=f"{marker} Demo table contract."),
            entity=table_reference,
            termsOfUse=Markdown(root="Demonstration use only."),
        ),
    }


def _refuse_foreign_contract(existing: Any, marker: str) -> None:
    if existing is None:
        return
    if marker not in model_str(getattr(existing, "description", "")):
        raise RuntimeError("Refusing to overwrite foreign data contract")


def run_scenario(namespace: str, table_fqn: str) -> None:
    """Create governance assets, their relations, and a guarded data contract."""
    marker = ownership_marker(namespace)
    table = Tables.retrieve_by_name(table_fqn)
    table_reference = EntityReference(**Tables.to_entity_reference(table))
    requests = build_requests(namespace, table_reference)

    existing_contract = DataContracts.get_by_entity(table.id, "table")
    _refuse_foreign_contract(existing_contract, marker)

    classification_fqn = f"{namespace}_classification"
    glossary_fqn = f"{namespace}_glossary"
    term_one_fqn = f"{glossary_fqn}.{namespace}_customer"
    term_two_fqn = f"{glossary_fqn}.{namespace}_account"
    domain_fqn = f"{namespace}_domain"
    data_product_fqn = f"{namespace}_customer_product"
    metric_one_fqn = f"{namespace}_customer_count"
    metric_two_fqn = f"{namespace}_active_customer_rate"
    contract_fqn = f"{table_fqn}.dataContract_{namespace}_customer_contract"

    entities = [
        owned_upsert(
            Classifications,
            classification_fqn,
            requests["classification"],
            marker,
        ),
        owned_upsert(
            Tags,
            f"{classification_fqn}.{namespace}_sensitive",
            requests["tag"],
            marker,
        ),
        owned_upsert(Glossaries, glossary_fqn, requests["glossary"], marker),
    ]
    term_one = owned_upsert(
        GlossaryTerms,
        term_one_fqn,
        requests["term_one"],
        marker,
    )
    term_two = owned_upsert(
        GlossaryTerms,
        term_two_fqn,
        requests["term_two"],
        marker,
    )
    entities.extend([term_one, term_two])
    GlossaryTerms.add_relation(term_one_fqn, term_two_fqn, "relatedTo")
    GlossaryTerms.relations_graph(term_one_fqn, depth=2)

    entities.append(owned_upsert(Domains, domain_fqn, requests["domain"], marker))
    data_product = owned_upsert(
        DataProducts,
        data_product_fqn,
        requests["data_product"],
        marker,
    )
    entities.append(data_product)
    metric_one = owned_upsert(
        Metrics,
        metric_one_fqn,
        requests["metric_one"],
        marker,
    )
    metric_two = owned_upsert(
        Metrics,
        metric_two_fqn,
        requests["metric_two"],
        marker,
    )
    entities.extend([metric_one, metric_two])
    Metrics.add_related_metrics(metric_one.id, [metric_two.id])
    metric_reference = EntityReference(**Metrics.to_entity_reference(metric_one))
    DataProducts.add_assets(data_product_fqn, [metric_reference])

    DataContracts.validate_request(requests["contract"])
    contract = owned_upsert(
        DataContracts,
        contract_fqn,
        requests["contract"],
        marker,
    )
    entities.append(contract)
    DataContracts.get_by_entity(table.id, "table")
    DataContracts.export_odcs(contract.id).as_yaml().execute()

    for entity in entities:
        print(f"ready fqn={model_str(entity.fullyQualifiedName)} id={model_str(entity.id)}")


def main() -> int:
    try:
        namespace, table_fqn = validate_environment()
        configure()
        try:
            run_scenario(namespace, table_fqn)
        finally:
            reset()
    except (ValueError, RuntimeError) as exc:
        print(f"governance scenario failed: {exc}")
        return 1
    except Exception as exc:
        print(f"governance scenario failed: {type(exc).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
