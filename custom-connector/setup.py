import os
from typing import Dict, Set

from setuptools import find_namespace_packages, setup

build_options = {"includes": ["_cffi_backend"]}

base_requirements = {
    "openmetadata-ingestion==0.12.2"
}

setup(
    name="custom-connector",
    version="0.0.1",
    url="https://open-metadata.org/",
    author="OpenMetadata Committers",
    license="Apache License 2.0",
    description="Ingestion Framework for OpenMetadata",
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    options={"build_exe": build_options},
    install_requires=list(base_requirements),
)
