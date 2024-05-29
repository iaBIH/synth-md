from setuptools import setup, find_packages

# Tested using python 3.6.4
# Read the list of requirements from the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Define the setup configuration (Name, version, packages and dependencies of the package)
setup(
    name='synthMD',
    version='0.01',
    packages=find_packages(),
    install_requires=requirements,
)
