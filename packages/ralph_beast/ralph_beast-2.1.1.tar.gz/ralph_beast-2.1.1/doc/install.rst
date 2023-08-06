==============
How to install
==============

Linux
---------------

The simplest way to install ralph beast is(you need curl):

  $ curl https://raw.github.com/allegro/ralph_beast/master/install.sh | bash -

or if you feel comfortable with pip:

  $ pip install ralph-beast



Windows
-------

We provide windows binary. Just Download `beast.exe` file and prepare the configuration file.

.. _beast.exe: https://github.com/allegro/ralph_beast/raw/master/beast_windows.zip

The configuration file should be placed in the same directory as ``beast.exe`` or home directory.
Config file should be contain such data  :ref:`config_file`


MacOS
---------------

Put on your console below command to install.::

  $ pip install ralph-beast

or: ::

  $ curl https://raw.github.com/allegro/ralph_beast/master/install.sh | bash -






Configuration
=============

Now you need configuration file. Create file 

~/.beast/config

Windows binary already contains the file inside directory.

Config file should contain such data  :ref:`config_file`


.. _config_file:

Config file - example
---------------------
::

  username="jan.kowalski"
  api_key="478457f9f32323201ebde8ef79cd9d3a028ced56747"
  url="https://ralph-url.com"
  version="0.9"
  
  
Obtaining api_key
---------------------

You can find you api_key by clicking on your username on the bottom of the ralph page and selecting API Key link from the menu on the left.
