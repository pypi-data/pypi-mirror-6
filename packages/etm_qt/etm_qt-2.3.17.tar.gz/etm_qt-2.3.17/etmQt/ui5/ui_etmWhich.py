# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './etmWhich.ui'
#
# Created: Mon Dec 16 08:37:38 2013
#      by: PyQt5 UI code generator 5.1.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_whichDialog(object):
    def setupUi(self, whichDialog):
        whichDialog.setObjectName("whichDialog")
        whichDialog.resize(436, 136)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(whichDialog.sizePolicy().hasHeightForWidth())
        whichDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(whichDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.theQuestion = QtWidgets.QLabel(whichDialog)
        self.theQuestion.setObjectName("theQuestion")
        self.gridLayout.addWidget(self.theQuestion, 0, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(whichDialog)
        self.comboBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(whichDialog)
        self.buttonBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(whichDialog)
        self.buttonBox.accepted.connect(whichDialog.accept)
        self.buttonBox.rejected.connect(whichDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(whichDialog)

    def retranslateUi(self, whichDialog):
        _translate = QtCore.QCoreApplication.translate
        whichDialog.setWindowTitle(_translate("whichDialog", "which"))
        self.theQuestion.setText(_translate("whichDialog", "You have selected instance ..."))

