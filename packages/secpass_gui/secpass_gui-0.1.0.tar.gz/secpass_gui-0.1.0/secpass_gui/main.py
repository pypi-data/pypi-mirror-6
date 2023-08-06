# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/04/19
# copy: (C) Copyright 2014-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import os
import wx
import argparse
import logging
import asset
from secpass import engine, api
from secpass.util import _

#------------------------------------------------------------------------------
class SecPassGui(object):

  #----------------------------------------------------------------------------
  def __init__(self, options):
    self.engine = engine.Engine(options.config)

  #----------------------------------------------------------------------------
  def start(self):
    self.app = wx.App(False)
    win   = wx.Frame(None, wx.ID_ANY, _('SecPass v{}', asset.version('secpass-gui')))
    panel = wx.Panel(win)
    text  = wx.StaticText(panel, label=_('SecPass GUI is under active development.'), pos=(40,30))
    win.Show(True)
    self.app.MainLoop()

#------------------------------------------------------------------------------
def main(args=None):

  cli = argparse.ArgumentParser(
    description = _('SecPass graphical user interface (GUI).'),
  )

  cli.add_argument(
    _('-v'), _('--verbose'),
    dest='verbose', action='count',
    default=int(os.environ.get('SECPASS_VERBOSE', '0')),
    help=_('increase logging verbosity (can be specified multiple times)'))

  cli.add_argument(
    _('-c'), _('--config'), metavar=_('FILENAME'),
    dest='config',
    default=os.environ.get('SECPASS_CONFIG', api.DEFAULT_CONFIG),
    help=_('configuration filename (current default: "{}")', '%(default)s'))

  options = cli.parse_args(args=args)

  # todo: share this with secpass?...
  # TODO: send logging to "log" window?... (is this done by wx???)
  rootlog = logging.getLogger()
  rootlog.setLevel(logging.WARNING)
  rootlog.addHandler(logging.StreamHandler())
  # TODO: add a logging formatter...
  # TODO: configure logging from config.ini?...
  if options.verbose == 1:
    rootlog.setLevel(logging.INFO)
  elif options.verbose > 1:
    rootlog.setLevel(logging.DEBUG)

  gui = SecPassGui(options)
  gui.start()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
