from setuptools import find_packages, setup

base_requirements = ["scipy"]

setup(name='custom-tests',
      version='0.0.1',
      description='OpenMetadata Custom Tests',
      packages=find_packages(),
      install_requires=list(base_requirements)
     )
