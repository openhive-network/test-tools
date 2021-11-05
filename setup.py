from setuptools import setup

setup(
    name='test_tools',
    description='Tools for testing hive software',
    url='https://gitlab.syncad.com/hive/test-tools',
    author='Piotr Batko',
    author_email='pbatko@syncad.com',
    packages=['test_tools'],
    package_dir={'': 'package'},
    install_requires=['requests'],
)
