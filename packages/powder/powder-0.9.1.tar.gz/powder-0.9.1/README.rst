========
 powder 
========

Introduction
------------

A python package to simulate powder diffraction using CCP4 and xprepx.


Home Page & Repository
----------------------

Home Page: https://pypi.python.org/pypi/powder/

Documentation: http://pythonhosted.org/powder/

Repository: https://github.com/jcstroud/powder


Example
-------

1. Make a new directory and put your pdb file in it.
2. Make a template settings file in that directory::

     powder -t > settings.cfg

3. Edit *at least* the first five values in the settings
   file on the right hand side of the "=" signs.

   **Important** - Don't change the names on the left
   of the "=" signs because the left hand side names have meaning.

4. Run *powder* with the config file you edited::

     powder settings.cfg


Testing Setup
~~~~~~~~~~~~~

You can test your setup in the test directory with the command::

     ./powder-test test.cfg

This allows testing after development without the need to build and install.

The ``-d`` flag is also available to prevent powder from running ccp4 and
xprepx during debugging.
