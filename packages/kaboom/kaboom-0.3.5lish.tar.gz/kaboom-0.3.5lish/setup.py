from distutils.core import setup
from kaboom import __version__

import os

description = 'Command line key-value store'
long_description = description
if os.path.exists('README.rst'):
    long_description = open('README.rst').read()


setup(
    name='kaboom',
    version=__version__,
    packages=['kaboom'],
    url='http://github.com/vinu76jsr/kaboom',
    author='vaibhav',
    author_email='vinu76jsr@gmail.com',
    license='bsd3',
    description=description,
    entry_points={'console_scripts': [
        'kaboom = kaboom.kaboom:run']},
    long_description=long_description,
    install_requires=["termcolor >= 1.1.1", ]
)
