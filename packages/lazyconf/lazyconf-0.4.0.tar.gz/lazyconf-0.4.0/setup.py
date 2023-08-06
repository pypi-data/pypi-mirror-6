import sys
from setuptools import setup

l = 'lazyconf/'
s = 'schema/'

setup(
    name='lazyconf',
    version='0.4.0',
    author='Fareed Dudhia',
    author_email='fareeddudhia@gmail.com',
    package_dir={'':'lazyconf'},
    packages=['lib'],
    py_modules=['lazyconf','console'],
    package_data={'': [ s + '*.json', s + '/*.json']},
    entry_points={
        'console_scripts': ['lazyconf = console:console',]},
    url='https://www.github.com/fmd/lazyconf',
    license='LICENSE.rst',
    description='Insultingly simple configuration for Python 2.7 applications.',
    long_description=open('README.rst').read(),
)
