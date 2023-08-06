TheAlot
-------

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
