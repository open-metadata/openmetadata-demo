#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from setuptools import setup, find_packages

base_requirements = {"openmetadata-ingestion~=1.7.0"}

setup(
    name="custom-connector",
    version="0.0.1",
    url="https://open-metadata.org/",
    author="OpenMetadata Committers",
    license="Apache License 2.0",
    description="Ingestion Framework for OpenMetadata",
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    install_requires=list(base_requirements),
    packages=find_packages(include=["connector", "connector.*"]),
)
