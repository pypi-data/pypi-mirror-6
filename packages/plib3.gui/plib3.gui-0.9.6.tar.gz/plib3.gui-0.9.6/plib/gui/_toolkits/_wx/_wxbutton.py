#!/usr/bin/env python3
"""
Module WXBUTTON -- Python wxWidgets Button Widgets
Sub-Package GUI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for button widgets.
"""

import wx
#import wx.lib.buttons

from plib.gui.defs import *
from plib.gui._widgets import button

from ._wxcommon import _PWxWidget, _wxstockids


class _PWxButtonMixin(object):
    
    def set_caption(self, caption):
        self.SetLabel(caption)
    
    def set_icon(self, pxname):
        # No way currently to set custom icons in wxWidgets (at least,
        # none that are worth considering here...)
        pass


class PWxButton(_PWxButtonMixin, _PWxWidget, wx.Button, button.PButtonBase):
    
    def __init__(self, parent, caption=None, pxname=None,
                 target=None, geometry=None):
        
        _id = -1
        # We can't wait until PButtonBase.__init__ to do this in wxWidgets
        if isinstance(caption, int):
            # 'caption' is actually an action key
            if caption in _wxstockids:
                _id = _wxstockids[caption]
                caption = None
        wx.Button.__init__(self, parent, _id)
        self._align = ALIGN_LEFT  # used by PWxPanel to determine placement
        button.PButtonBase.__init__(self, caption, pxname, target, geometry)


class PWxCheckBox(_PWxButtonMixin, _PWxWidget, wx.CheckBox,
                  button.PCheckBoxBase):
    
    fn_get_checked = 'GetValue'
    fn_set_checked = 'SetValue'
    
    def __init__(self, parent, caption=None, pxname=None, tristate=False,
                 target=None, geometry=None):
        
        if tristate:
            style = wx.CHK_3STATE
        else:
            style = wx.CHK_2STATE
        wx.CheckBox.__init__(self, parent, style=style)
        self._align = ALIGN_LEFT  # used by PWxPanel to determine placement
        button.PCheckBoxBase.__init__(self, caption, pxname, tristate,
                                      target, geometry)
        
        # Pass our current checked state in the visible SIGNAL_TOGGLED signal
        self.setup_notify(SIGNAL_CHECKTOGGLED, self.OnCheckToggled)
    
    def OnCheckToggled(self, event):
        # The event wrapper will fill in our checked state
        self.do_notify(SIGNAL_TOGGLED)
    
    def make_tristate(self):
        # This is done in the constructor in wxWidgets
        pass
