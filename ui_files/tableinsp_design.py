# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tableinsp_design.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(996, 786)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(160, 0, 831, 751))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tableWidget = QtWidgets.QTableWidget(self.tab)
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 831, 731))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tabWidget.addTab(self.tab, "")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 20, 160, 161))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.openButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.openButton.setObjectName("openButton")
        self.verticalLayout.addWidget(self.openButton)
        self.addButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.addButton.setObjectName("addButton")
        self.verticalLayout.addWidget(self.addButton)
        self.delButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.delButton.setObjectName("delButton")
        self.verticalLayout.addWidget(self.delButton)
        self.plotButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.plotButton.setObjectName("plotButton")
        self.verticalLayout.addWidget(self.plotButton)
        self.helpButton = QtWidgets.QPushButton(self.centralwidget)
        self.helpButton.setGeometry(QtCore.QRect(0, 720, 161, 23))
        self.helpButton.setObjectName("helpButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 996, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TableInspector"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "стр. 1"))
        self.openButton.setText(_translate("MainWindow", "Открыть"))
        self.addButton.setText(_translate("MainWindow", "Добавить"))
        self.delButton.setText(_translate("MainWindow", "Удалить"))
        self.plotButton.setText(_translate("MainWindow", "Построить график"))
        self.helpButton.setText(_translate("MainWindow", "Руководство"))