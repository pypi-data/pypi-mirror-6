from distutils.core import setup
import os
import sys

sys.path.insert(0, os.path.abspath('.'))

setup(
    name='kaboom',
    version='0.1.4',
    packages=[''],
    url='http://github.com/vinu76jsr/kaboom',
    license='',
    author='vaibhav',
    author_email='vinu76jsr@gmail.com',
    description='Command line key-value store',
    install_requires=['rethinkdb'],
    entry_points={'console_scripts': [
        'kaboom = kaboom:run']}
)
