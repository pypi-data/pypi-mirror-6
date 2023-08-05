#!/usr/bin/env python3
"""
Module QT4COMMON -- Python Qt 4 Common Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common Qt 4 GUI objects for use by the other
Qt 4 modules.
"""

from abc import ABCMeta

from PyQt4 import Qt as qt

from plib.gui.defs import *

_qtalignmap = {
    ALIGN_LEFT: qt.Qt.AlignLeft | qt.Qt.AlignVCenter,
    ALIGN_CENTER: qt.Qt.AlignCenter,
    ALIGN_RIGHT: qt.Qt.AlignRight | qt.Qt.AlignVCenter
}

_qtcolormap = dict(
    (color, qt.QColor(color.lower()))
    for color in COLORNAMES
)

_qtmessagefuncs = {
    MBOX_INFO: qt.QMessageBox.information,
    MBOX_WARN: qt.QMessageBox.warning,
    MBOX_ERROR: qt.QMessageBox.critical,
    MBOX_QUERY: qt.QMessageBox.question
}

_qtsignalmap = {
    SIGNAL_ACTIVATED: "triggered()",
    SIGNAL_CLICKED: "clicked()",
    SIGNAL_TOGGLED: "toggled(bool)",
    SIGNAL_SELECTED: "activated(int)",
    SIGNAL_LISTSELECTED: "currentItemChanged(QTreeWidgetItem*, QTreeWidgetItem*)",
    SIGNAL_CELLSELECTED: "currentCellChanged(int, int, int, int)",
    SIGNAL_TABLECHANGED: "cellChanged(int, int)",
    SIGNAL_TEXTCHANGED: "textChanged()",  # textEdited()?
    SIGNAL_EDITCHANGED: "textChanged(const QString&)",  # textEdited(const QString&)?
    SIGNAL_ENTER: "returnPressed()",
    SIGNAL_TABCHANGED: "currentChanged(int)",
    SIGNAL_NOTIFIER: "activated(int)",
    SIGNAL_BEFOREQUIT: "aboutToQuit()"
}

_qteventmap = {
    SIGNAL_CELLCHANGED: "tableCellChanged",
    SIGNAL_TEXTSTATECHANGED: "textStateChanged",
    SIGNAL_FOCUS_IN: "focusInEvent",
    SIGNAL_FOCUS_OUT: "focusOutEvent",
    SIGNAL_CLOSING: "closeEvent",
    SIGNAL_SHOWN: "showEvent",
    SIGNAL_HIDDEN: "hideEvent"
}


def _qtmap(signal):
    if signal in _qtsignalmap:
        return qt.SIGNAL(_qtsignalmap[signal])
    elif signal in _qteventmap:
        return qt.SIGNAL(_qteventmap[signal])
    else:
        return None


# Ugly hack to fix metaclass conflict for classes that use the collection
# ABCs

_QtMeta = type(qt.QObject)


class _PQtMeta(ABCMeta, _QtMeta):
    
    def __init__(cls, name, bases, attrs):
        _QtMeta.__init__(cls, name, bases, attrs)
        ABCMeta.__init__(cls, name, bases, attrs)


# NOTE: we don't need to define 'wrapper' methods here as we do under GTK and
# wxWidgets because Qt silently discards any extra parameters that are not
# accepted by a signal handler. (BTW, this is good because wrappers don't seem
# to work like they should in Qt -- see PEDIT.PY, PEditor._setup_signals.)

class _PQtCommunicator(object):
    """Mixin class to abstract signal/slot functionality in Qt.
    """
    
    def setup_notify(self, signal, target):
        qt.QObject.connect(self, _qtmap(signal), target)
    
    def do_notify(self, signal, *args):
        sig = _qtmap(signal)
        if sig is not None:
            self.emit(sig, *args)
    
    _emit_event = do_notify


class _PQtWidgetBase(object):
    """Mixin class to provide common Qt widget methods.
    """
    
    fn_enable_get = 'isEnabled'
    fn_enable_set = 'setEnabled'
    
    _palette = None
    
    def update_widget(self):
        self.update()
    
    def preferred_width(self):
        return max(self.minimumSize().width(), self.sizeHint().width())
    
    def preferred_height(self):
        return max(self.minimumSize().height(), self.sizeHint().height())
    
    def set_width(self, width):
        self.resize(width, self.height())
    
    def set_height(self, height):
        self.resize(self.width(), height)
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self.move(left, top)
    
    def _mapped_color(self, color):
        if isinstance(color, qt.QColor):
            return color
        return _qtcolormap[color]
    
    def set_colors(self, fg=None, bg=None):
        palette = qt.QPalette(self.palette())
        if fg is not None:
            palette.setColor(self.foregroundRole(), self._mapped_color(fg))
        if bg is not None:
            self.setAutoFillBackground(True)
            palette.setColor(self.backgroundRole(), self._mapped_color(bg))
        self.setPalette(palette)
    
    def set_foreground_color(self, color):
        self.set_colors(fg=color)
    
    def set_background_color(self, color):
        self.set_colors(bg=color)
    
    def get_font_name(self):
        return self.font().family()
    
    def get_font_size(self):
        return self.font().pointSize()
    
    def get_font_bold(self):
        return self.font().bold()
    
    def get_font_italic(self):
        return self.font().italic()
    
    def _qt_font_object(self, font_name, font_size, bold, italic):
        font = qt.QFont(font_name, font_size)
        font.setBold(bold)
        font.setItalic(italic)
        return font
    
    def _set_font_object(self, font_name, font_size, bold, italic):
        self.setFont(self._qt_font_object(
            font_name, font_size, bold, italic))
    
    def set_focus(self):
        self.setFocus()


class _PQtWidget(_PQtCommunicator, _PQtWidgetBase):
    """Mixin class for Qt widgets that can send/receive signals.
    """
    
    def focusInEvent(self, event):
        self.widget_class.focusInEvent(self, event)
        self._emit_event(SIGNAL_FOCUS_IN)
    
    def focusOutEvent(self, event):
        self.widget_class.focusOutEvent(self, event)
        self._emit_event(SIGNAL_FOCUS_OUT)


class _PQtClientWidget(_PQtWidget):
    """Mixin class for Qt main window client widgets.
    """
    pass
