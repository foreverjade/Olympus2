# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Form_TradingStatus.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form_TradingStatus(object):
    def setupUi(self, Form_TradingStatus):
        Form_TradingStatus.setObjectName("Form_TradingStatus")
        Form_TradingStatus.resize(699, 656)
        self.groupBox_PnL = QtWidgets.QGroupBox(Form_TradingStatus)
        self.groupBox_PnL.setGeometry(QtCore.QRect(10, 10, 681, 211))
        self.groupBox_PnL.setObjectName("groupBox_PnL")
        self.tableView_PnL = QtWidgets.QTableView(self.groupBox_PnL)
        self.tableView_PnL.setGeometry(QtCore.QRect(10, 20, 661, 181))
        self.tableView_PnL.setObjectName("tableView_PnL")
        self.groupBox_Position = QtWidgets.QGroupBox(Form_TradingStatus)
        self.groupBox_Position.setGeometry(QtCore.QRect(10, 230, 681, 171))
        self.groupBox_Position.setObjectName("groupBox_Position")
        self.tableView_Position = QtWidgets.QTableView(self.groupBox_Position)
        self.tableView_Position.setGeometry(QtCore.QRect(10, 20, 661, 141))
        self.tableView_Position.setObjectName("tableView_Position")
        self.groupBox_TradingHistory = QtWidgets.QGroupBox(Form_TradingStatus)
        self.groupBox_TradingHistory.setGeometry(QtCore.QRect(10, 410, 681, 201))
        self.groupBox_TradingHistory.setObjectName("groupBox_TradingHistory")
        self.tableView_TradingHistory = QtWidgets.QTableView(self.groupBox_TradingHistory)
        self.tableView_TradingHistory.setGeometry(QtCore.QRect(10, 20, 661, 171))
        self.tableView_TradingHistory.setObjectName("tableView_TradingHistory")
        self.pushButton_Hide = QtWidgets.QPushButton(Form_TradingStatus)
        self.pushButton_Hide.setGeometry(QtCore.QRect(600, 620, 93, 31))
        self.pushButton_Hide.setObjectName("pushButton_Hide")
        self.pushButton_Refresh = QtWidgets.QPushButton(Form_TradingStatus)
        self.pushButton_Refresh.setGeometry(QtCore.QRect(10, 620, 93, 31))
        self.pushButton_Refresh.setObjectName("pushButton_Refresh")

        self.retranslateUi(Form_TradingStatus)
        QtCore.QMetaObject.connectSlotsByName(Form_TradingStatus)

    def retranslateUi(self, Form_TradingStatus):
        _translate = QtCore.QCoreApplication.translate
        Form_TradingStatus.setWindowTitle(_translate("Form_TradingStatus", "TradingStatus"))
        self.groupBox_PnL.setTitle(_translate("Form_TradingStatus", "PnL"))
        self.groupBox_Position.setTitle(_translate("Form_TradingStatus", "Position"))
        self.groupBox_TradingHistory.setTitle(_translate("Form_TradingStatus", "Trading History"))
        self.pushButton_Hide.setText(_translate("Form_TradingStatus", "Hide"))
        self.pushButton_Refresh.setText(_translate("Form_TradingStatus", "Refresh"))
