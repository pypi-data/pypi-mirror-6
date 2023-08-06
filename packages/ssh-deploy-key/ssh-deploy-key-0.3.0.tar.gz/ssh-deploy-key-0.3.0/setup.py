from setuptools import setup

setup(
    name='ssh-deploy-key',
    version='0.3.0',
    author='Travis Bear',
    author_email='travis_bear@yahoo.com',
    keywords = "ssh remote deploy key",
    scripts=['bin/ssh-deploy-key',],
    url='https://grinder_to_graphite.readthedocs.org/en/latest/',
    license='LICENSE.txt',
    description='Deploys your ssh key easily to a single remote host.  Deploys it rapidly to many remote hosts.',
    long_description=open('README.txt').read(),
    packages=['ssdk'],
    install_requires=["colorama", "paramiko"]
)
