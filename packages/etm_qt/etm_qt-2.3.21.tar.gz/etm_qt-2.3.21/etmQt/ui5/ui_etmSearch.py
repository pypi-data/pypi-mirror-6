# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './etmSearch.ui'
#
# Created: Sun Dec  8 18:13:57 2013
#      by: PyQt5 UI code generator 5.1.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.NonModal)
        Form.resize(186, 33)
        Form.setStyleSheet("font-size: 10pt")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.previous = QtWidgets.QToolButton(Form)
        self.previous.setStyleSheet("border: 0px")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/previous.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.previous.setIcon(icon)
        self.previous.setIconSize(QtCore.QSize(18, 18))
        self.previous.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.previous.setAutoRaise(True)
        self.previous.setObjectName("previous")
        self.horizontalLayout.addWidget(self.previous)
        self.search = QtWidgets.QLineEdit(Form)
        self.search.setMinimumSize(QtCore.QSize(120, 0))
        self.search.setStyleSheet("padding: 0px")
        self.search.setObjectName("search")
        self.horizontalLayout.addWidget(self.search)
        self.next = QtWidgets.QToolButton(Form)
        self.next.setStyleSheet("border: 0px")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/next.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.next.setIcon(icon1)
        self.next.setIconSize(QtCore.QSize(18, 18))
        self.next.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.next.setAutoRaise(True)
        self.next.setObjectName("next")
        self.horizontalLayout.addWidget(self.next)

        self.retranslateUi(Form)
        self.search.returnPressed.connect(self.next.animateClick)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Search"))
        self.previous.setToolTip(_translate("Form", "Click here or press Shift Ctrl-G to search backward."))
        self.previous.setText(_translate("Form", "&Previous"))
        self.search.setPlaceholderText(_translate("Form", "Search"))
        self.next.setToolTip(_translate("Form", "Click here or press Ctrl-G to search forward."))
        self.next.setText(_translate("Form", "&Next"))

