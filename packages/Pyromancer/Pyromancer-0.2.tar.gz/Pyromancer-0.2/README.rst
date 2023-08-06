Simple framework for creating IRC bots.

Example
~~~~~~~

.. code:: python

    from pyromancer.objects import Pyromancer

    HOST = '1.2.3.4'
    PORT = 6667
    NICK = 'PyromancerBot'

    settings = {'host': HOST, 'port': PORT, 'nick': NICK, 'encoding': 'ISO-8859-1',
                'packages': ['.test_examples']}

    p = Pyromancer(settings)
    p.run()

Custom commands
~~~~~~~~~~~~~~~

Writing own commands is fairly simple. Create a folder which will be the
package name, with a folder named "commands" in it and a module to hold
the commands in there. In your module, you can register functions to be
a command with the built-in command decorator. After that you need to
register it in your settings, and you can use it.

Example
^^^^^^^

File layout:

::

    test/
        commands/
            __init__.py
            test_commands.py
        __init__.py
    init.py

test\_commands.py:

.. code:: python

    from pyromancer.decorators import command

    @command(r'bye (.*)')
    def bye(match):
        return 'Bye {m[1]}!'

init.py:

.. code:: python

    settings['packages'] = ['test.test_commands']

On IRC:

::

    <User> bye everyone
    <Bot> Bye everyone!

Pyromancer scans the modules in the settings automatically for functions
decorated using the commands decorator, so all your commands in
``test_commands.py`` are used automatically.

The ``command`` decorator
^^^^^^^^^^^^^^^^^^^^^^^^^

You must apply this to a function to mark it as a command. It will be
used when scanning for and collecting commands.

Parameters
''''''''''

-  ``patterns`` - a regular expression or a list of expressions. When a
   list is given, all patterns are attempted when matching the input,
   and only when all patterns in the list fail to match, the command is
   not executed.
   ``python @command(['hi', 'hello']) def hi(match):     return 'Hello!'``

-  ``prefix`` - a boolean which defaults to ``True``. When true, the
   command pattern is only attempted to match when the message line
   starts with the prefix defined in the settings of the bot. This is
   useful for commands which are very bot-like (in contrary to commands
   which look and behave like natural language). Using a boolean and a
   setting allows the same command to be triggered in different ways,
   depending on the settings of the bot which installed the command
   package.

Messaging from a command
^^^^^^^^^^^^^^^^^^^^^^^^

Messaging from inside the function which makes up the command is as easy
as can be for simple use cases, but can be done in numerous ways for the
more complex situations.

Most of the times, arguments are passed to the ``Match.msg`` function,
which applies formatting by default and provides some additional
utilities. The most important of those is that when no target has been
passed on as an argument, it will use either the channel or the user (in
case of a PM) whose input line triggered the command to be executed as
the target, effectively replying.

Parameters
''''''''''

-  ``message`` - the message to be send to the server. Formatting will
   be applied using any additional ``args`` and ``kwargs``, so you can
   apply the full power of the `Python Format
   Mini-Language <http://docs.python.org/3.3/library/string.html#format-string-syntax>`__
   on the message.

-  ``args`` and ``kwargs`` - arguments to be passed on through the
   formatting which is applied on ``message``.

Methods of messaging
''''''''''''''''''''

-  Return a ``message``
   ``python @command(r'bye (.*)') def bye(match):     return 'Bye {m[1]}!'``

-  Return a tuple of ``message`` and optional ``args`` and ``kwargs`` to
   be used when formatting ``message``. ``args`` can be both a list of
   arguments, or simply all the middle elements of the tuple.
   ``python def gibberish(match):     return 'A = {}, B = {}, C = {c_char}', 'a', 'b', {'c_char': 'c'}``

-  Yield a ``message`` or a tuple of ``message`` and optional ``args``
   and ``kwargs``. Yielding can be done as much as you want, which is
   the easiest way of sending multiple messages from one command.
   ``python @command(r'say (.*)') def say(match):     for part in match[1].split(', '):         yield 'Saying {}', part``

-  Return a list of ``message`` or a tuple of ``message`` and optional
   ``args`` and ``kwargs``.
   ``python def hi(match):     return ['Hi', 'Hello']``

-  Use ``Match.msg``. This is the only way to benefit from the
   non-default functionalities provided by this function.
   ``python def raw(match):     match.msg('Raw {} message {m[1]}', raw=True)``

Extra parameters for ``Match.msg``
''''''''''''''''''''''''''''''''''

-  ``target`` - the target to send the message to. If not provided, it
   will attempt to use either the channel or user whose input line
   triggered the command, which effectively results in replying.

-  ``raw`` - defaults to ``False``. When true, no formatting is applied
   on ``message``.

Dependencies
~~~~~~~~~~~~

-  `irc <https://pypi.python.org/pypi/irc>`__

To do
~~~~~

-  Ability to process raw lines through custom commands
-  Figure out how to do translation of messages through the
   ``Match.msg`` function.
-  Add timers
-  Make a module of settings (like Django), with settings for each
   installed package prioritized based on place in packages setting (not
   like Django).
-  Add a command module which keeps track of channels joined and users
   in them which other commands can use.
-  Redo commands loading so you can use ``commands.py`` for custom
   commands instead of a mandatory ``commands`` directory.
-  Redo package loading so you just have to specify the package name and
   it loads the commands and any future things like settings.

Changelist
~~~~~~~~~~

0.2 - 2014-03-14
^^^^^^^^^^^^^^^^

-  Add tests
-  Add multiple and easier ways to send messages from a command.
-  Add support for multiple patterns for the same command.
-  Add a configurable command prefix setting for the more bot-like
   commands.
-  Trying to access a word in a ``Line`` now correctly returns an empty
   string when the index does not exist.
-  Fix passing positional arguments to ``Match.msg`` not working
   properly.

0.1 - 2013-11-17
^^^^^^^^^^^^^^^^

-  Initial release

