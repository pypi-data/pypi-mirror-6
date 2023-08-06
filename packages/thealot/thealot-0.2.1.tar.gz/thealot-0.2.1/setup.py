from setuptools import setup
setup(name='thealot',
      version='0.2.1',
      author='Edvin "nCrazed" Malinovskis',
      author_email='edvin.malinovskis@gmail.com',
      url='https://github.com/nCrazed/TheAlot',
      description='A lightweight IRC bot framework.',
      long_description=open("README.rst").read(),
      packages=['thealot', 'thealot.plugins'],
      install_requires=[
          'irc',
          'sqlalchemy'
          ],
      package_data={
          '':['config.json'],
          },
      )
