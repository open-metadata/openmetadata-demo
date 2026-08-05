"""Repository-wide contracts for the maintained OpenMetadata 2.0 examples."""

import json
import re
from importlib import import_module
from pathlib import Path

import pytest
import yaml
from metadata.config.common import load_config_file
from metadata.generated.schema.metadataIngestion.workflow import (
    OpenMetadataWorkflowConfig,
)

ROOT = Path(__file__).parents[1]
INGESTION_VERSION = "2.0.0.0rc1"
DOCKER_VERSION = "2.0.0-rc1"
RELEASE_VERSION = "2.0.0-rc1-release"
MAINTAINED_ROOTS = (
    ROOT / "custom-connector",
    ROOT / "custom-graphql",
    ROOT / "dynamic_csv_importer",
    ROOT / "api-lineage-cicd",
    ROOT / "ingestion-automation",
    ROOT / "mcp",
)
CONTRACT_FILES = (
    ROOT / "README.md",
    ROOT / "pyproject.toml",
    ROOT / ".lychee.toml",
)


def maintained_text_files() -> list[Path]:
    """Return customer-facing text files while ignoring generated local state."""
    ignored_parts = {".pytest_cache", "__pycache__", "node_modules"}
    allowed_suffixes = {
        ".cfg",
        ".ini",
        ".js",
        ".json",
        ".md",
        ".py",
        ".sql",
        ".toml",
        ".yaml",
        ".yml",
    }
    return [
        path
        for root in MAINTAINED_ROOTS
        for path in root.rglob("*")
        if path.is_file()
        and (path.suffix.lower() in allowed_suffixes or path.name == "Dockerfile")
        and not ignored_parts.intersection(path.parts)
    ]


def repository_contract_files() -> list[Path]:
    """Return every file whose OpenMetadata pin is part of the support contract."""
    return [
        *maintained_text_files(),
        *CONTRACT_FILES,
        *(path for path in (ROOT / ".github").rglob("*") if path.is_file()),
    ]


def pin_contract_violations(paths: list[Path]) -> list[str]:
    """Return dependency, image, and release references that are not exact RC pins."""
    exact_package = re.compile(
        rf"openmetadata-ingestion(?:\[[^]]+\])?\s*==\s*{re.escape(INGESTION_VERSION)}\b"
    )
    image_candidate = re.compile(
        r"(?:(?:[A-Za-z0-9_.-]+(?::[0-9]+)?/)*openmetadata/(?:ingestion|server|postgresql)"
        r"|openmetadata-demo/ingestion)"
    )
    exact_image = re.compile(
        rf"(?:docker\.getcollate\.io/openmetadata/(?:ingestion|server|postgresql)"
        rf"|openmetadata-demo/ingestion):{re.escape(DOCKER_VERSION)}\b"
    )
    release_candidate = "OpenMetadata/releases/download/"
    exact_release = re.compile(
        rf"OpenMetadata/releases/download/{re.escape(RELEASE_VERSION)}/docker-compose"
    )
    violations = []

    for path in paths:
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            installed_version_check = re.search(
                r"version\(\s*['\"]openmetadata-ingestion['\"]\s*\)", line
            )
            checks = (
                (
                    "openmetadata-ingestion" in line and not installed_version_check,
                    exact_package,
                    "Python dependency",
                ),
                (bool(image_candidate.search(line)), exact_image, "Docker image"),
                (release_candidate in line, exact_release, "Compose release"),
            )
            for is_candidate, exact_pattern, kind in checks:
                if is_candidate and not exact_pattern.search(line):
                    violations.append(f"{path}:{line_number}: unpinned {kind}: {line.strip()}")
    return violations


def test_custom_connector_workflows_validate_and_resolve_classes(monkeypatch) -> None:
    """All eight workflows must use 2.0 models and an importable custom class."""
    monkeypatch.setenv("OPENMETADATA_HOST", "http://localhost:8585/api")
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")
    configs = sorted((ROOT / "custom-connector/configs").glob("*.yaml"))

    assert len(configs) == 8
    for path in configs:
        raw = load_config_file(path)
        OpenMetadataWorkflowConfig.model_validate(raw)
        class_path = raw["source"]["serviceConnection"]["config"]["sourcePythonClass"]
        module_name, class_name = class_path.rsplit(".", maxsplit=1)
        assert getattr(import_module(module_name), class_name)


def test_yaml_and_json_files_parse() -> None:
    """Every maintained structured-data file must remain syntactically valid."""
    for path in maintained_text_files():
        if path.suffix in {".yaml", ".yml"}:
            yaml.safe_load(path.read_text())
        elif path.suffix == ".json":
            json.loads(path.read_text())


def test_openmetadata_dependencies_are_pinned_to_the_exact_rc() -> None:
    """Reject stale or floating OpenMetadata package, image, and release pins."""
    contract_files = repository_contract_files()
    package_pattern = re.compile(
        r"openmetadata-ingestion(?:\[[^]]+\])?\s*"
        r"(==|~=|>=|<=|>|<)\s*([A-Za-z0-9_.-]+)"
    )
    image_pattern = re.compile(
        r"docker\.getcollate\.io/openmetadata/(?:ingestion|server):([A-Za-z0-9_.-]+)"
    )
    release_pattern = re.compile(r"OpenMetadata/releases/download/([A-Za-z0-9_.-]+)/docker-compose")

    package_constraints: set[tuple[str, str]] = set()
    image_versions: set[str] = set()
    release_versions: set[str] = set()
    rc_literal_pattern = re.compile(r"\b2\.0\.0(?:\.0)?(?:rc\d+|-rc\d+)(?:-release)?\b")
    rc_literals: set[str] = set()
    for path in contract_files:
        contents = path.read_text()
        package_constraints.update(package_pattern.findall(contents))
        image_versions.update(image_pattern.findall(contents))
        release_versions.update(release_pattern.findall(contents))
        rc_literals.update(rc_literal_pattern.findall(contents))

    assert package_constraints == {("==", INGESTION_VERSION)}
    assert image_versions == {DOCKER_VERSION}
    assert release_versions == {RELEASE_VERSION}
    assert rc_literals == {INGESTION_VERSION, DOCKER_VERSION, RELEASE_VERSION}
    assert pin_contract_violations(contract_files) == []


@pytest.mark.parametrize(
    "reference",
    [
        "openmetadata-ingestion",
        "openmetadata-ingestion>=2.0.0.0rc1",
        "openmetadata-ingestion==${OPENMETADATA_VERSION}",
        "docker.getcollate.io/openmetadata/ingestion:${OPENMETADATA_VERSION}",
        "docker.getcollate.io/openmetadata/server",
        "openmetadata/ingestion:latest",
        "openmetadata/server:2.0.0-rc1",
        "ghcr.io/openmetadata/server:2.0.0-rc1",
        "OpenMetadata/releases/download/${OPENMETADATA_VERSION}/docker-compose-postgres.yml",
    ],
)
def test_pin_contract_rejects_unpinned_references(tmp_path: Path, reference: str) -> None:
    """Candidate detection must not rely on another correctly pinned occurrence."""
    candidate = tmp_path / "candidate.txt"
    candidate.write_text(reference)

    assert pin_contract_violations([candidate])


def test_maintained_examples_do_not_contain_credential_shaped_literals() -> None:
    """Credentials in maintained examples must be supplied through the environment."""
    yaml_files = [
        path for root in MAINTAINED_ROOTS for path in (*root.rglob("*.yaml"), *root.rglob("*.yml"))
    ]
    jwt_literal = re.compile(r"jwtToken:\s*(?!\$\{OPENMETADATA_JWT_TOKEN\})\S+")
    token_shapes = (
        re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    )

    for path in maintained_text_files():
        contents = path.read_text()
        assert not any(pattern.search(contents) for pattern in token_shapes), path
    for path in yaml_files:
        assert not jwt_literal.search(path.read_text()), path


def test_mcp_seed_credentials_match_the_workshop() -> None:
    """The seed must reuse the documented Compose database user safely."""
    seed = (ROOT / "mcp/resources/postgres-script.sql").read_text()
    workshop = (ROOT / "mcp/README.md").read_text()

    assert "CREATE USER openmetadata_user" not in seed
    assert "GRANT pg_read_all_stats TO openmetadata_user;" in seed
    assert "DROP VIEW IF EXISTS public.actor_view;" in seed
    assert "DROP TABLE IF EXISTS public.sensitive_customers;" in seed
    assert "mcp/resources/postgres-script.sql" in workshop
    assert "-v ON_ERROR_STOP=1" in workshop
    assert "`openmetadata_password`" in workshop
