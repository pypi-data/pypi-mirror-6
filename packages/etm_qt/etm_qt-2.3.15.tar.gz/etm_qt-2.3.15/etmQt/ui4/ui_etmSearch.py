# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './etmSearch.ui'
#
# Created: Sun Dec  8 19:40:52 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.setWindowModality(QtCore.Qt.NonModal)
        Form.resize(186, 33)
        Form.setStyleSheet(_fromUtf8("font-size: 10pt"))
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setMargin(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.previous = QtGui.QToolButton(Form)
        self.previous.setStyleSheet(_fromUtf8("border: 0px"))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/previous.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.previous.setIcon(icon)
        self.previous.setIconSize(QtCore.QSize(18, 18))
        self.previous.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.previous.setAutoRaise(True)
        self.previous.setObjectName(_fromUtf8("previous"))
        self.horizontalLayout.addWidget(self.previous)
        self.search = QtGui.QLineEdit(Form)
        self.search.setMinimumSize(QtCore.QSize(120, 0))
        self.search.setStyleSheet(_fromUtf8("padding: 0px"))
        self.search.setObjectName(_fromUtf8("search"))
        self.horizontalLayout.addWidget(self.search)
        self.next = QtGui.QToolButton(Form)
        self.next.setStyleSheet(_fromUtf8("border: 0px"))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/next.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.next.setIcon(icon1)
        self.next.setIconSize(QtCore.QSize(18, 18))
        self.next.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.next.setAutoRaise(True)
        self.next.setObjectName(_fromUtf8("next"))
        self.horizontalLayout.addWidget(self.next)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.search, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.next.animateClick)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Search", None))
        self.previous.setToolTip(_translate("Form", "Click here or press Shift Ctrl-G to search backward.", None))
        self.previous.setText(_translate("Form", "&Previous", None))
        self.search.setPlaceholderText(_translate("Form", "Search", None))
        self.next.setToolTip(_translate("Form", "Click here or press Ctrl-G to search forward.", None))
        self.next.setText(_translate("Form", "&Next", None))

