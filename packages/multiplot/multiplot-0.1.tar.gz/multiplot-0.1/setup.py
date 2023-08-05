# encoding: utf-8
from setuptools import setup

# read long_description from README.rst
long_description = None
try:
    long_description = open('README.rst').read()
    long_description += '\n' + open('CHANGES.rst').read()
except IOError:
    pass

setup(
    name='multiplot',
    version='0.1',
    description='Squeeze multiple image files into one page',
    long_description=long_description,
    author='Thomas Gläßle',
    author_email='t_glaessle@gmx.de',
    url='https://github.com/coldfix/multiplot',
    license='Public Domain',
    py_modules=['multiplot'],
    entry_points={
        'console_scripts': [
            'multiplot = multiplot:main'
        ],
    },
    install_requires=['docopt'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    ],
)
