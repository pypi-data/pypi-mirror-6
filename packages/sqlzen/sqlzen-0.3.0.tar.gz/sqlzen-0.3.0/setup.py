from setuptools import setup


__version__ = "0.3.0"


setup(name='sqlzen',
      version=__version__,
      description='Because sometimes you want raw SQL',
      author='Charles Reese',
      author_email='charlespreese@gmail.com',
      url='https://github.com/creese/sqlzen',
      download_url=(
          'https://github.com/creese/sqlzen/archive/' + __version__ + '.zip'),
      packages=['sqlzen'],
      install_requires=[
          'SQLAlchemy',
          'functions==0.3.0'],)
