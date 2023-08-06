from setuptools import setup
import functions

setup(name='functions',
      version=functions.__version__,
      description='Functional programming in Python',
      author='Charles Reese',
      author_email='charlespreese@gmail.com',
      url='https://github.com/creese/functions',
      download_url=('https://github.com/creese/functions/archive/' +
                    functions.__version__ + '.zip'),
      packages=['functions'],)
