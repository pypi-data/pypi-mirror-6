from distutils.core import setup

from to_function import __version__

setup(name='to_function',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Convert a callable to a function.',
      url='https://github.com/tlevine/to_function',
      packages=['to_function'],
      install_requires = [],
      tests_require = ['nose'],
      version=__version__,
      license='AGPL',
)
