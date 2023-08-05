#!/usr/bin/env python3
"""
Module PYSIDETABWIDGET -- Python PySide Tab Widget
Sub-Package GUI.TOOLKITS.PYSIDE of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide GUI objects for the tab widget.
"""

from PySide import QtGui as qt

from plib.gui._widgets import tabwidget

from ._pysidecommon import _PQtSequenceMeta, _PQtClientWidget


class PQtTabWidget(_PQtClientWidget, qt.QTabWidget,
                   tabwidget.PTabWidgetBase, metaclass=_PQtSequenceMeta):
    
    def __init__(self, parent, tabs=None, target=None):
        self._item = None
        self._target = None
        self._setting_index = False
        qt.QTabWidget.__init__(self, parent)
        tabwidget.PTabWidgetBase.__init__(self, parent, tabs, target)
    
    def count(self, value):
        # Method name collision, we want it to be the Python sequence
        # count method here.
        return tabwidget.PTabWidgetBase.count(self, value)
    
    def __len__(self):
        # Let this method access the Qt tab widget count method.
        return qt.QTabWidget.count(self)
    
    def _get_tabtitle(self, index):
        return str(self.tabText(index))
    
    def _set_tabtitle(self, index, title):
        self.setTabText(index, str(title))
    
    def _add_tab(self, index, title, widget):
        self.insertTab(index, widget, str(title))
    
    def _del_tab(self, index):
        self.removeTab(index)
    
    def current_index(self):
        return self.currentIndex()
    
    def _current_changed(self, index):
        # Wrapper for tab changed signal.
        if (not self._setting_index) and self._target:
            self._target(index)
    
    def connect_to(self, target):
        # Hack to capture double firing of tab changed signal when
        # tab is changed programmatically instead of by user
        self._target = target
        tabwidget.PTabWidgetBase.connect_to(self, self._current_changed)
    
    def set_current_index(self, index):
        # Wrap the call to avoid double calling of signal handler, then
        # make the call by hand.
        self._setting_index = True
        self.setCurrentIndex(index)
        self._setting_index = False
        self._current_changed(index)
