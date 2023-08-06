from setuptools import setup

setup(
    name='ssh-deploy-key',
    version='0.4.0',
    author='Travis Bear',
    author_email='travis_bear@yahoo.com',
    keywords = "ssh remote deploy key",
    scripts=['bin/ssh-deploy-key',],
    url='https://grinder_to_graphite.readthedocs.org/en/latest/',
    license='LICENSE.txt',
    description='Fast and easy deployment of ssh keys to remote hosts',
    long_description=open('README.txt').read(),
    packages=['ssdk'],
    install_requires=[
        "colorama",
        "paramiko >= 1.13.0"
    ]
)
