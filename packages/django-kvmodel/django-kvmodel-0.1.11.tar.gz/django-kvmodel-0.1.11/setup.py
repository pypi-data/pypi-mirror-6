from setuptools import setup

description = 'A package that helps creating django key-value models easily.'

try:
    with open('README.rst') as f:
        long_description = f.read()
except IOError:
    long_description = description

try:
    with open('LICENSE') as f:
        license = f.read()
except IOError:
    license = 'MIT License'

setup(
    name='django-kvmodel',
    version='0.1.11',
    description=description,
    author='Abdallah Dorra',
    author_email='amdorra@gmail.com',
    url='https://github.com/amdorra/django-kvmodel',
    license=license,
    long_description=long_description,
    packages=['kvmodel'],
    install_requires=['django >= 1.2.7'],
)
