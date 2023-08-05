from setuptools import setup

setup(
    name='ssh-deploy-key',
    version='develop',
    author='Travis Bear',
    author_email='travis_bear@yahoo.com',
    keywords = "ssh remote deploy key",
    scripts=['bin/ssh-deploy-key',],
    url='https://grinder_to_graphite.readthedocs.org/en/latest/',
    license='LICENSE.txt',
    description='Deploys your ssh key to one or more remote hosts, in parallel.',
    long_description=open('README.txt').read(),
    install_requires=["colorama", "paramiko"]
)
