from setuptools import setup


__version__ = "0.5.1"


setup(name='functions',
      version=__version__,
      description='Functional programming in Python',
      author='Charles Reese',
      author_email='charlespreese@gmail.com',
      url='https://github.com/creese/functions',
      download_url=(
          'https://github.com/creese/functions/archive/' + __version__ + '.zip'),
      packages=['functions'],)
