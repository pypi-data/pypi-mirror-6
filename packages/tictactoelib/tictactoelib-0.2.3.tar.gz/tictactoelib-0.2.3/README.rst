Game Logic for Ultimate Tic Tac Toe
===================================

This library allows to easily create front-ends for ultimate-tic-tac-toe game.
It takes care of game rules, validating the arguments, calling the right
functions.

``run.lua`` is an example how this library can be used. To try out::

    tictactoelib/run.lua \
        tictactoelib/examples/dumb_player.lua \
        tictactoelib/examples/dumb_player.lua

The file takes two arguments: Lua files, which implement a player.
``tictactoelib/examples/dumb_player.lua`` is a demo player which marks a first
available slot.  Command-line example above makes it fight with itself.

See comments in ``tictactoelib/examples/dumb_player.lua`` how to implement a
player (it could also be something that takes events from UI).

For human-readable game rules, see ultimate-tic-tac-toe's website_.

Compatibility
-------------

Library is written in pure Lua, is tested to be compatible with Lua5.1, Lua5.2
and luajit.

.. _website: http://mathwithbaddrawings.com/2013/06/16/ultimate-tic-tac-toe/
