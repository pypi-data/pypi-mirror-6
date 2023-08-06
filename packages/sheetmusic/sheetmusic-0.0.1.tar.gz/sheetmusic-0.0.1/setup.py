from distutils.core import setup

from libsheetmusic import __version__

setup(name='sheetmusic',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Functions to be loaded by the Gnumeric Sheetmusic plugin',
      url='https://github.com/tlevine/sheetmusic',
      packages=['libsheetmusic'],
      scripts=['bin/sheetmusic-installer'],
      install_requires = [],
      tests_require = ['nose'],
      version=__version__,
      license='AGPL',
)
