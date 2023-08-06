# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/geoff/work/baserip/baserip/ui/br_jobdock.ui'
#
# Created: Fri Jan 17 20:40:49 2014
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

class Ui_BR_JobDock(object):
    def setupUi(self, BR_JobDock):
        BR_JobDock.setObjectName(_fromUtf8("BR_JobDock"))
        BR_JobDock.resize(254, 174)
        BR_JobDock.setFloating(True)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayoutWidget = QtGui.QWidget(self.dockWidgetContents)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 231, 134))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_2 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.lblTimeLeft = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblTimeLeft.setText(_fromUtf8(""))
        self.lblTimeLeft.setObjectName(_fromUtf8("lblTimeLeft"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lblTimeLeft)
        self.label_3 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_3)
        self.lblFileSize = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblFileSize.setText(_fromUtf8(""))
        self.lblFileSize.setObjectName(_fromUtf8("lblFileSize"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.lblFileSize)
        self.label_4 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_4)
        self.lblTimeEncoded = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblTimeEncoded.setText(_fromUtf8(""))
        self.lblTimeEncoded.setObjectName(_fromUtf8("lblTimeEncoded"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.lblTimeEncoded)
        self.label_5 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_5)
        self.lblPass = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblPass.setObjectName(_fromUtf8("lblPass"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.lblPass)
        self.verticalLayout.addLayout(self.formLayout)
        self.progressBar = QtGui.QProgressBar(self.verticalLayoutWidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnCancel = QtGui.QPushButton(self.verticalLayoutWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/application-exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnCancel.setIcon(icon)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout.addWidget(self.btnCancel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        BR_JobDock.setWidget(self.dockWidgetContents)

        self.retranslateUi(BR_JobDock)
        QtCore.QMetaObject.connectSlotsByName(BR_JobDock)

    def retranslateUi(self, BR_JobDock):
        BR_JobDock.setWindowTitle(_translate("BR_JobDock", "Baserip Job", None))
        self.label_2.setText(_translate("BR_JobDock", "Real Time Left:", None))
        self.label_3.setText(_translate("BR_JobDock", "Estimated File Size:", None))
        self.label_4.setText(_translate("BR_JobDock", "Time Encoded:", None))
        self.label_5.setText(_translate("BR_JobDock", "Pass:", None))
        self.lblPass.setText(_translate("BR_JobDock", "0 of 0", None))
        self.btnCancel.setText(_translate("BR_JobDock", "Cancel", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    BR_JobDock = QtGui.QDockWidget()
    ui = Ui_BR_JobDock()
    ui.setupUi(BR_JobDock)
    BR_JobDock.show()
    sys.exit(app.exec_())

