from setuptools import setup, find_packages

setup(
    name='p_final',
    version='0.1',
    packages=find_packages(where='src/main'),
    package_dir={'': 'src/main'},
)
