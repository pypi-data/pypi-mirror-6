from setuptools import setup, find_packages

import configuration_panda

with open('requirements.txt') as requirements_doc:
    requirements = requirements_doc.read()

setup(
    name="configuration-panda",
    packages=find_packages(),
    version=configuration_panda.__version__,
    author="Mike Dunn",
    author_email="mike@eikonomega.com",
    url="https://github.com/eikonomega/configuration_panda",
    description="ConfigurationPanda provides easy loading and access to "
                "the data elements of JSON based configuration files.",
    long_description=configuration_panda.__doc__,

    install_requires=requirements,
    #include_package_data=True,
    package_data={
        '': ['requirements.txt']
    }
)

