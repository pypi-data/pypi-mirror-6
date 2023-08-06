=====
radio
=====

**radio** is a python script to just listen to the radio using mplayer.

Installation
============

Use::

    $ sudo pip install radio

Usage
=====

Listen to the radio::

    $ radio <radio_id>

where <radio_id> must be in radio.lists.urls.

List available radios::

    $ radio -l
    
Turn off the radio by pressing "q" (as it uses mplayer).

Add more radios just editing lists/radios.py

To do
=====

- make command for adding radios more easily, perhaps using doit
- support multiples lists
- use curl instead mplayer if available
- use cvlc instead mplayer if available


Author
======

* Santiago Pestarini <santiagonob@gmail.com>

Copyright
=========

radio is licensed under the *do What The Fuck you want to Public License*, WTFPL. See the LICENSE file.

