from distutils.core import setup

from pluplusch import __version__

setup(name='pluplusch',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Big dada: Download data from lots of open data platforms.',
      url='https://github.com/tlevine/pluplusch',
      packages=['pluplusch'],
      install_requires = ['picklecache','requests','pickle_warehouse'],
      tests_require = ['nose'],
      version=__version__,
      license='AGPL',
)
