
from PySide import QtCore, QtGui

class DetailsTable(QtGui.QTableWidget):
    def __init__(self, parent):
        QtGui.QTableWidget.__init__(self, parent.widget)

        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setObjectName("choiceTable")
        
        self.setColumnCount(2)
        self.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem())
        self.horizontalHeaderItem(0).setText("Name")
        
        self.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem())
        self.horizontalHeaderItem(1).setText("Date")

        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setStretchLastSection(True)
        parent.verticalLayout.addWidget(self)
        
    def addLine(self, text, progress=0):
        id = self.rowCount()
        self.insertRow(id)
        
        item = QtGui.QTableWidgetItem(text)
        item.setCheckState(QtCore.Qt.Unchecked)
        self.setItem(id, 1, item)
        
