manage.py
=========

Human friendly CLI builder.

.. image:: https://drone.io/github.com/Birdback/manage.py/status.png
    :target: https://drone.io/github.com/Birdback/manage.py

Installation
------------

``pip install manage.py``


Quickstart
----------

``cat manage.py``

.. code:: python

    from manager import Manager

    manager = Manager()

    @manager.command
    def echo(text, capitalyze=False):
        """print the given <name>"""
        if capitalyze:
            text = text.upper()
        return text

    if __name__ == '__main__':
        manager.main()

``manage --help``::

    usage: manage [<namespace>.]<command> [<args>]

    positional arguments:
      command     the command to run

    optional arguments:
      -h, --help  show this help message and exit

    available commands:
      echo        print the given <name>


``manage echo --help``::

    $ manage echo --help

    usage: manage [-h] [--capitalyze] text

    print the given <name>

    positional arguments:
      text          no description

    optional arguments:
      -h, --help    show this help message and exit
      --capitalyze  no description


Managers
--------

Managers can be used together by merging them

.. code:: python

    from third_party import manager

    my_app_manager.merge(manager)

    # Merge within a new namespace:
    my_app_manager.merge(manager, namespace='third_party')


Commands
--------

Commands can be organized within namespaces

.. code:: python

    @manager.command(namespace='config')
    def set(key, value):
        # ...


Arguments
---------

Argument definition can be overridden

.. code:: python

    @manager.arg('first_arg', help='this is help for first arg')
    @manager.command
    def my_command(first_arg):
        # ...


Arguments can be prompted

.. code:: python

    @manager.prompt('password', hidden=True, confirm=True)
    @manager.command
    def connect(username, password):
        # ...


Environment
-----------

Environment variables can be sourced from a ``.env`` file as ``key=value`` pair.

Environment variable can be enforce using ``Manager.env`` decorator

.. code:: python

    @manager.env('MY_ENV_VAR')
    @manager.command
    def my_command():
        return os.environ['MY_ENV_VAR']
