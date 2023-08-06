# encoding: utf8

from setuptools import setup

setup(
    name='python-mongoql-conv',
    version="0.0",
    url='https://pypi.python.org/pypi/mongoql-conv/',
    description='Library to convert those MongoDB queries to something else, like a python expresion, a function or a Django Q object tree to be used with a ORM query.',
    long_description='''Use `mongoql-conv <https://pypi.python.org/pypi/mongoql-conv/>`_ instead.''',
    author='Ionel Cristian M\xc4\x83rie\xc8\x99',
    platforms=['all'],
    zip_safe=False,
    author_email='contact@ionelmc.ro',
    install_requires=['mongoql-conv'],
)
