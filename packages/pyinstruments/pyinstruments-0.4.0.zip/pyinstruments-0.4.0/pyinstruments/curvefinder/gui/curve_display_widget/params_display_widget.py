from PyQt4 import QtCore, QtGui

class ParamsDisplayWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ParamsDisplayWidget, self).__init__(parent)
        self.lay = QtGui.QVBoxLayout()
        self.tree = QtGui.QTreeWidget()
        self.tree.setSortingEnabled(True)
        self.lay.addWidget(self.tree)
        self.setLayout(self.lay)
        self.tree.setHeaderLabels(["column name", "value"])
        self.tree.setColumnWidth(0,150)
        self.tree.setColumnWidth(1,150)
        self.setMinimumWidth(200)
    
    def format_nicely(self, val):
        return str(val)[:255]
    
    def display_curve(self, curve):
        self.tree.clear()
        for name, val in curve.params.iteritems():
            self.tree.addTopLevelItem(QtGui.QTreeWidgetItem([name, self.format_nicely(val)]))
        

