"""
Project setup
"""
import os

from setuptools import find_namespace_packages, find_packages, setup


def get_long_description():
    root = os.path.dirname(__file__)
    with open(os.path.join(root, "README.md")) as f:
        description = f.read()
    return description


base_requirements = {"pydantic", "requests", "openmetadata-ingestion~=0.13"}
dev = {"isort", "black", "pycln"}

setup(
    name="om-rename",
    version="0.0.1",
    description="Service rename helper.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    zip_safe=True,
    include_package_data=True,
    packages=find_namespace_packages(),
    entry_points={
        "console_scripts": ["rename = rename.main:cli"],
    },
    install_requires=list(base_requirements),
    extras_require={
        "dev": list(dev),
    },
)
