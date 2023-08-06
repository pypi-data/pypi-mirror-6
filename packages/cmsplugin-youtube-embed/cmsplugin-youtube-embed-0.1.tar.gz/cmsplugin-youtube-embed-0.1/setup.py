import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='cmsplugin-youtube-embed',
    version='0.1',
    packages=['cmsplugin_youtube'],
    license='BSD License',  # example license
    description='A simple Django app to embed youtube videos into the cms.',
    long_description=README,
    author='Danie Tate',
)
