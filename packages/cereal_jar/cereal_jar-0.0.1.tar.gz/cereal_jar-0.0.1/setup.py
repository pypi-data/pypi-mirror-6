from distutils.core import setup

from cereal_jar import __version__

setup(name='cereal_jar',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Save things in [cookie] jar format',
      url='https://github.com/tlevine/jar',
      packages=['cereal_jar'],
      install_requires = [],
      tests_require = ['nose'],
      version=__version__,
      license='AGPL',
)
