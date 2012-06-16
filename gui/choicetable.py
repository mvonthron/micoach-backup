
from PySide import QtCore, QtGui

class ChoiceTable(QtGui.QTableWidget):
    def __init__(self, parent):
        QtGui.QTableWidget.__init__(self, parent)

        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setObjectName("choiceTable")
        
        self.setColumnCount(5)
        self.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(3, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(4, QtGui.QTableWidgetItem())
        
        self.horizontalHeaderItem(0).setText("Date")
        self.horizontalHeaderItem(1).setText("Name")
        self.horizontalHeaderItem(2).setText("Activity")
        self.horizontalHeaderItem(3).setText("Duration")
        self.horizontalHeaderItem(4).setText("Distance")

        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setStretchLastSection(True)
        
        
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
        self.setItem(id, 4, QtGui.QTableWidgetItem(entry['distance']))
        
