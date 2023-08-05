
=======
Reversi
=======

An implementation of the popular Reversi board game, for use by one or two
players. Some simple AI is included to provide a computer opponent, and if you
are feeling lazy you can watch while two AI opponents slug it out.

Installation
============

For Version 1.2, supported platforms are Linux and now Windows (tested on Win7), 
although *in theory* this game should play equally well on Mac. I would like to
hear from anyone who can help with porting (I don't have a Mac, or a Mac OS to 
hand).

System Requirements:
--------------------

    *   Python 3

    *   Numpy for Python 3

Installation (Linux):
---------------------

    0.  Ensure all dependencies are installed. In particular, make sure you have
        a version of python >= 3.2, with the `numpy <http://www.numpy.org/>`_ 
        package installed. 

    1.  Unzip the tar.gz somewhere.

    2.  In a console window navigate to the Reversi-1.2 directory and run the
        following command as root (on Ubuntu/Debian use sudo):

            ``[sudo] python3 setup.py install``

    3.  On Ubuntu a desktop launcher is installed, which you should be able to
        find in the Dash and drag to the launcher bar. The default assumes you 
        are using python 3.2. If this is not the case you will need to manually 
        tweak the path references in the .desktop file.

Installation (Windows):
-----------------------

    0.  Ensure all dependencies are installed. In particular, make sure you have
        a version of python >= 3.2, and numpy. The easiest way to do this on 
        Windows is to install `WinPython <http://code.google.com/p/winpython/>`_
        for your system, because (in addition to numpy) loads of commonly-used 
        packages are bundled with python ready to use.

    1.  Extract the tar.gz somewhere (7-Zip should work).
    
    2.  Navigate into the dist directory and extract the Reversi-1.2.zip file.

    3.  In a console window navigate to the Reversi-1.2 directory and run the
        following command:

            ``[path_to_python\\]python setup.py install``

    4.  A .bat launch script is installed in the public desktop. This should 
        work on both XP and Win 7/8 systems, but the path references may need
        to be edited for your flavour of python installation. The default 
        assumes WinPython 3.3.2.3 for amd64 (see note above).

Controls
========

The controls for the game are minimal, and hopefully self-explanatory, but here
is a list:

Preparation Controls:
---------------------

    Language:
        A selection box appears to enable the player to choose their
        preferred language.

        If no language is selected the game will default to English.

    Your name:
        You can type anything you like here, it just helps to distinguish
        the players.

    Mode:
        Four modes are supported:

            n.  Normal (human versus computer opponent).

            p.  Person versus Person, in 'hot-seat' mode.

            c.  Computer versus computer, what I like to call TV mode.

            b.  Benchmarking mode, all graphics turned off. In this mode
                additional information is requested for the number of games
                to play.

        The default mode is 'Normal'.

    Token:
        The game asks the first player to choose a token, Black or White.
        Click your choice or type 'b' or 'w', depending on UI (see below).

Game Play Controls:
-------------------

Who starts is chosen at random.

    Choose Tile:
        Depending on UI this is achieved by either clicking on the appropriate
        tile, or typing in the tile coordinates as a space-separated pair of
        numbers, e.g., ``5 6``

    Hints:
        A hint mode is provided for each (human) player that can be toggled
        by either typing 'h' or clicking the appropriate button, depending
        on the UI you are using.

    Quit:
        Typing 'q', hitting 'Esc' and/or clicking the 'Close Window' icon
        (the details depend on the UI) causes the current game to be aborted.

    Play Again:
        You can elect to play again as many times as you want. The more
        games you play, your game statistics will be accumulated and
        displayed on the scoreboard.

        At the time of writing, there is no mechanism for storing game
        statistics between sessions, so if you want to save your high-scores you
        will have to resort to a screen-shot!

Choice of UI: Console vs. Tkinter/ttk
=====================================

The game has been shipped 'hard-wired' for the tkinter/ttk interface. For most
purposes this is (I believe) a nice and easy interface to use. However,
particularly if you want to do a lot of bench-testing of different AI, you may
wish to use the console interface instead. This is very easy do in the source
code, just un-comment the console interface and comment the tkinter interface in
the heading of the ``ui`` module.

An older version of the game also had a pygame interface, but this has been
removed in the shipped version. There are several reasons for this:

    *   At the time of writing, installing pygame for Python 3 is still
        something of a black art. It was felt that the difficulty of installing
        pygame outweighs any advantages of using it for a simple board game for
        end users.

    *   Removing the pygame interface makes the packaging simpler (OK, so I'm
        lazy).

    *   For a board game, the sophisticated handling of sprites (pygame's great
        strength) is not required. Tkinter/ttk offers instead a very good set of
        themed widgets with excellent hooks for callouts, making the ui very
        easy to write, and much nicer to use, than is possible with the graphics
        of pygame.

    *   At the time of writing, pygame does not support unicode. This means that
        i18n with languages like, for example, Chinese, is not possible in a
        pygame interface using the Python i18n package. You just end up with a
        load of rectangular boxes on the screen. i18n with pygame is still
        possible, but it would require a lot of code, and the use of a lot of
        graphic images instead of text. As noted above, I am lazy.

        *sigh* Why, in this day and age, is software being written that does not
        support unicode (expecially when that is one of the strengths of the
        language it is written in)?

Some history:
=============

This implementation of Reversi is *very* loosely based on the Reversi game
described in the book *Invent Your Own Computer Games With Python* by 'Al
Sweigart <http://inventwithpython.com/>'_. While some of the algorithms may
still be recognisable, this code has been designed from scratch from an object
model rather than using the functional programming flow diagram approach.

Originally implemented with a console UI, the code was adapted to work with
both pygame and tkinter/ttk graphics. However, due to lack of support in pygame
for unicode, the pygame interface was dropped to enable i18n (see above for the
polemic).

I have had a lot of fun designing some more intelligent AI for the more
demanding player, although I expect this still falls well below
tournament standard. Nevertheless, the result is more pleasing to my eye, and
hopefully more bug-free and maintainable. The AI is designed to be pluggable, so
it should be relatively easy to create new algorithms and implement them in
future versions.

As you might have guessed from the citation above, my original motive for
writing this was to learn Python. However, as I went along the project became a
vehicle for learning a lot of other associated Pythonic stuff.

This little game introduced me to Pygame and NumPy, and then tkinter/ttk.
In the later stages I found out how to use the i18n module for
internationalization.

This project has been an opportunity for me to (re-)learn Eclipse, and an
introduction to NetBeans. I have also looked at some other IDEs aimed
specifically at Python, but I have not (yet) found one that will stay alive long
enough to type 'Hello World!'.

I have also found out a lot I never wanted to know about CVS, and a lot I am
very grateful to have discovered about Mercurial.

I have used this little piece of code to find out more about
distributing Python software. If you are reading this, you will know I have
succeeded :).

Finally, because I don't allow Windows computers in the house, I have learned 
one heck of a lot about using VirtualBox while I was testing/debugging the 
Windows installation. I also re-discovered why I hate Windows...

Languages
=========

At time of writing the only options supported are English, French and Chinese,
but if there is someone 'out there' interested in helping with other
translations I will be happy to hear from them.

I would also be grateful for any help with my rusty French and 'Google
Translate' Chinese :).

Author:
=======

Bob Bowles <bobjohnbowles@gmail.com>

