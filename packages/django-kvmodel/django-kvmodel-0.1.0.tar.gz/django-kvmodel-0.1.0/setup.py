from setuptools import setup

description = 'A package that helps creating django key-value models easily.'

try:
    with open('README.rst') as f:
        long_description = f.read()
except IOError:
    long_description = description

setup(
    name='django-kvmodel',
    version='0.1.0',
    description=description,
    author='Abdallah Dorra',
    author_email='amdorra@gmail.com',
    url='https://github.com/amdorra/django-kvmodel',
    license='LICENSE.txt',
    long_description=long_description,
    packages=['kvmodel'],
    install_requires=['django >= 1.2.7'],
)
