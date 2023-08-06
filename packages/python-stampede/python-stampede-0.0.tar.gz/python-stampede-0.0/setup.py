# encoding: utf8

from setuptools import setup

setup(
    name='python-stampede',
    version="0.0",
    url='https://pypi.python.org/pypi/stampede/',
    description='Event-loop based, miniature job queue and worker that runs the task in a subprocess (via fork).',
    long_description='''Use `stampede <https://pypi.python.org/pypi/stampede/>`_ instead.''',
    author='Ionel Cristian M\xc4\x83rie\xc8\x99',
    platforms=['all'],
    zip_safe=False,
    author_email='contact@ionelmc.ro',
    install_requires=['stampede'],
)
