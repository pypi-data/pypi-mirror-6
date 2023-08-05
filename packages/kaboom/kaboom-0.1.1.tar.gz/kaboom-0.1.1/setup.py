from distutils.core import setup
import os
import sys

sys.path.insert(0, os.path.abspath('lib'))

setup(
    name='kaboom',
    version='0.1.1',
    packages=[''],
    url='http://github.com/vinu76jsr/kaboom',
    license='',
    author='vaibhav',
    author_email='vinu76jsr@gmail.com',
    description='Command line key-value store',
    install_requires=['rethinkdb']
)
