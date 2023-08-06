===================
Secure Password GUI
===================

A GUI interface to secpass, the Secure Password system.

.. WARNING::

  2014/04/19: The SecPass GUI package is currently under active
  development, i.e. it is not ready for use. Come back in a month
  or two.


TL;DR
=====

Install on Linux (for non-Ubuntu distributions, adjust as needed):

.. code-block:: bash

  # install wxPython 3.0.0.0

  $ wget http://downloads.sourceforge.net/project/wxpython/wxPython/3.0.0.0/wxPython-src-3.0.0.0.tar.bz2
  $ tar xvjf wxPython-src-3.0.0.0.tar.bz2
  $ cd wxPython-src-3.0.0.0/wxPython
  $ python build-wxpython.py --install
    # if building into a virtualenv, add "--installdir=$VIRTUAL_ENV" to the last line

  # install secpass-gui

  $ pip install secpass-gui

  # run secpass-gui

  $ secpass-gui
