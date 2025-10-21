from setuptools import find_packages, setup

setup(
    name="openmetadata-user-updater-connector",
    version="1.0.0",
    description="Custom OpenMetadata connector to update user entities from GraphQL",
    author="OpenMetadata Demo",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "openmetadata-ingestion==1.9.11",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
