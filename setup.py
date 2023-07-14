from setuptools import setup, find_packages

# tested using python 3.6.4
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='synthMD',
    version='0.01',
    packages=find_packages(),
    install_requires=requirements,
)