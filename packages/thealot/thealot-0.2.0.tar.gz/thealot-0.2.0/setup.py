"""
TheAlot
-----

TheAlot is a modular IRC bot framework for Python3.

Install
```````

.. code:: bash

    pip install thealot

Configure
`````````

.. code:: json

    {
        "server"    : "irc.quakenet.org",
        "port"      : 6667,
        "channel"   : "#TheAlot",
        "nickname"  : "TestAlot",
        "prefix"    : "!",
        "database"  : "sqlite:///alot.db",
        "plugins"   : [
        ]
    }

Run
```

.. code:: bash

    python -m thealot.thealot

or

.. code:: python

    from thealot import TheAlot

    bot = TheAlot()

    if __name__ == "__main__":
        bot.start()

"""
from setuptools import setup
setup(name='thealot',
      version='0.2.0',
      author='Edvin "nCrazed" Malinovskis',
      author_email='edvin.malinovskis@gmail.com',
      url='https://github.com/nCrazed/TheAlot',
      description='A lightweight IRC bot framework.',
      long_description=__doc__,
      packages=['thealot', 'thealot.plugins'],
      install_requires=[
          'irc',
          'sqlalchemy'
          ],
      package_data={
          '':['config.json'],
          },
      )
