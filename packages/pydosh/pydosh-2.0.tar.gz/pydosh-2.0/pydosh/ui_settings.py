# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings.ui'
#
# Created: Wed Dec 18 15:05:17 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.resize(708, 364)
        self.gridLayout_2 = QtGui.QGridLayout(Settings)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtGui.QSpacerItem(23, 28, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 0, 1, 1, 1)
        self.addButton = QtGui.QToolButton(Settings)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addButton.setIcon(icon)
        self.addButton.setObjectName("addButton")
        self.gridLayout_2.addWidget(self.addButton, 1, 1, 1, 1)
        self.frame = QtGui.QFrame(Settings)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.view = QtGui.QTableView(self.frame)
        self.view.setObjectName("view")
        self.gridLayout.addWidget(self.view, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame, 0, 0, 4, 1)
        self.deleteButton = QtGui.QToolButton(Settings)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.deleteButton.setIcon(icon1)
        self.deleteButton.setObjectName("deleteButton")
        self.gridLayout_2.addWidget(self.deleteButton, 2, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(23, 217, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 3, 1, 1, 1)
        self.widget_4 = QtGui.QWidget(Settings)
        self.widget_4.setObjectName("widget_4")
        self.hboxlayout = QtGui.QHBoxLayout(self.widget_4)
        self.hboxlayout.setContentsMargins(0, -1, 0, -1)
        self.hboxlayout.setObjectName("hboxlayout")
        spacerItem2 = QtGui.QSpacerItem(136, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem2)
        self.saveButton = QtGui.QPushButton(self.widget_4)
        self.saveButton.setObjectName("saveButton")
        self.hboxlayout.addWidget(self.saveButton)
        self.revertButton = QtGui.QPushButton(self.widget_4)
        self.revertButton.setObjectName("revertButton")
        self.hboxlayout.addWidget(self.revertButton)
        self.closeButton = QtGui.QPushButton(self.widget_4)
        self.closeButton.setObjectName("closeButton")
        self.hboxlayout.addWidget(self.closeButton)
        self.gridLayout_2.addWidget(self.widget_4, 4, 0, 1, 1)

        self.retranslateUi(Settings)
        QtCore.QMetaObject.connectSlotsByName(Settings)
        Settings.setTabOrder(self.saveButton, self.revertButton)
        Settings.setTabOrder(self.revertButton, self.closeButton)
        Settings.setTabOrder(self.closeButton, self.addButton)
        Settings.setTabOrder(self.addButton, self.deleteButton)

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QtGui.QApplication.translate("Settings", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setToolTip(QtGui.QApplication.translate("Settings", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Add code</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("Settings", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteButton.setToolTip(QtGui.QApplication.translate("Settings", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Delete code</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteButton.setText(QtGui.QApplication.translate("Settings", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("Settings", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.revertButton.setText(QtGui.QApplication.translate("Settings", "&Revert", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("Settings", "&Close", None, QtGui.QApplication.UnicodeUTF8))

import pydosh_rc
