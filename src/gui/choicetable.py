
from PySide import QtCore, QtGui

class ChoiceTable(QtGui.QTableWidget):
    def __init__(self, parent):
        QtGui.QTableWidget.__init__(self, parent)

        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setObjectName("choiceTable")
        
        self.setColumnCount(6)
        self.checkAllBox = QtGui.QCheckBox(self.horizontalHeader())
        self.checkAllBox.stateChanged.connect(self.checkUncheckAll)
        self.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(3, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(4, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(5, QtGui.QTableWidgetItem())
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        
        self.horizontalHeaderItem(0).setText("Date")
        self.horizontalHeaderItem(1).setText("Name")
        self.horizontalHeaderItem(2).setText("Activity")
        self.horizontalHeaderItem(3).setText("Duration")
        self.horizontalHeaderItem(4).setText("Distance")
        self.horizontalHeaderItem(5).setText("ID")
        self.setColumnHidden(5, True)

        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(True)

        
    def addLine(self, entry, isNew=False):
        id = self.rowCount()
        self.insertRow(id)
        
        item = QtGui.QTableWidgetItem(entry['date'])
        if isNew:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)
        
        self.setItem(id, 0, item)
        self.setItem(id, 1, QtGui.QTableWidgetItem(entry['name']))
        self.setItem(id, 2, QtGui.QTableWidgetItem(entry['activity']))
        self.setItem(id, 3, QtGui.QTableWidgetItem(entry['time']))
        self.setItem(id, 4, QtGui.QTableWidgetItem(str(entry['distance'])))
        self.setItem(id, 5, QtGui.QTableWidgetItem(str(entry['id'])))
        
    def getCheckedId(self):
        checked = []
        for line in range(self.rowCount()):
            if self.item(line, 0).checkState():
                checked.append(int(self.item(line, 5).text()))
        
        return checked

    def checkUncheckAll(self, check):
        for line in range(self.rowCount()):
            self.item(line, 0).setCheckState(QtCore.Qt.CheckState(check))

    def resizeEvent(self, event=None):
        super(QtGui.QTableWidget, self).resizeEvent(event)
        self.checkAllBox.setGeometry(QtCore.QRect(3, 3, 18, 18))
