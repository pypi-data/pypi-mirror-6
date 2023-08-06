import sys
from setuptools import setup

l = 'lazyconf/'
s = 'schema/'

setup(
    name='lazyconf',
    version='0.3.9',
    author='Fareed Dudhia',
    author_email='fareeddudhia@gmail.com',
    package_dir={'':'lazyconf'},
    packages=['lib'],
    py_modules=['lazyconf','console'],
    entry_points={
        'console_scripts': ['lazyconf = console:console',]},
    data_files=[(s, [l + s +'django.json', l + s + 'empty.json'])],
    url='https://www.github.com/fmd/lazyconf',
    license='LICENSE.rst',
    description='Insultingly simple configuration for Python 2.7 applications.',
    long_description=open('README.rst').read(),
)
