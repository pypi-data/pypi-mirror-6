from distutils.core import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='Kinder',
    version='0.1.2',
    author='John J. Wang',
    author_email='john@zinc.io',
    packages=['kinder'],
    scripts=[],
    url='',
    license=read('LICENSE'),
    description='Probabilistic testing framework.',
    long_description=read('README.md'),
    install_requires=[
        "unittest >= 1.0.0"
        ],
    )
