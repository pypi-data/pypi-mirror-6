from distutils.core import setup
from kaboom import __version__


setup(
    name='kaboom',
    version=__version__,
    packages=['kaboom'],
    url='http://github.com/vinu76jsr/kaboom',
    author='vaibhav',
    author_email='vinu76jsr@gmail.com',
    license='bsd3',
    description='Command line key-value store',
    entry_points={'console_scripts': [
        'kaboom = kaboom.kaboom:run']}
)
