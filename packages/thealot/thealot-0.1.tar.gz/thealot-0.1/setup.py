from setuptools import setup
setup(name='thealot',
      version='0.1',
      author='Edvin "nCrazed" Malinovskis',
      author_email='edvin.malinovskis@gmail.com',
      url='https://github.com/nCrazed/TheAlot',
      packages=['thealot', 'thealot.plugins'],
      install_requires=[
          'irc',
          'sqlalchemy'
          ]
      )
