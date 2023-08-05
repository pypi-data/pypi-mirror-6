# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


def read(relative):
    contents = open(relative, 'r').read()
    return [l for l in contents.split('\n') if l != '']


setup(
    name='hayrack',
    version=read('VERSION')[0],
    description="""
    A tool for capturing messages from STDIN, such as when run as a program
    destination by Syslog-NG, and then load balance these messages over ZeroMQ
    to downstream worker nodes for processing.""",
    author='Steven Gonzales',
    author_email='steven.gonzales@rackspace.com',
    tests_require=read('./tools/test-requires'),
    install_requires=read('./tools/pip-requires'),
    test_suite='nose.collector',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup'])
)
