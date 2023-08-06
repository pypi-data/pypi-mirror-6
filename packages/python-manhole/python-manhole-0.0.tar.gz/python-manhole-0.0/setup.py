# encoding: utf8

from setuptools import setup

setup(
    name='python-manhole',
    version="0.0",
    url='https://pypi.python.org/pypi/manhole/',
    description='Inpection manhole for python applications. Connection is done via unix domain sockets.',
    long_description='''Use `manhole <https://pypi.python.org/pypi/manhole/>`_ instead.''',
    author='Ionel Cristian M\xc4\x83rie\xc8\x99',
    platforms=['all'],
    zip_safe=False,
    author_email='contact@ionelmc.ro',
    install_requires=['manhole'],
)
