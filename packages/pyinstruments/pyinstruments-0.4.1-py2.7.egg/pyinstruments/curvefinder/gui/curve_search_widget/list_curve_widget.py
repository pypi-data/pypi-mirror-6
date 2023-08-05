from pyinstruments.curvestore.models import CurveDB, Tag
from pyinstruments.curvefinder.gui.plot_window import get_window
from pyinstruments.curvefinder import _APP
from pyinstruments.curvestore.tag_edit_list_widget import TAG_COMPLETER

from curve.fitting import FitFunctions

from PyQt4 import QtCore, QtGui
import functools
import numpy
from StringIO import StringIO
import pandas


class MyItem(QtGui.QTreeWidgetItem):
    def __init__(self, curve):
        super(MyItem, self).__init__([str(curve.id), curve.name, str(curve.date)])
        self.pk = curve.pk
        self.ghost = False
        if curve.has_childs:
            for child in curve.childs.all():
                item_child = MyItem(child)
                self.addChild(item_child)
                
    def update(self, curve):
        self.ghost = False
        self.pk = curve.pk
        self.setText(0, str(curve.id))
        self.setText(1, curve.name)
        self.setText(2, str(curve.date))
        
        if curve.has_childs:
            child_items = dict([(self.child(index).pk, self.child(index)) for index in range(self.childCount())])
            for child in curve.childs.all():
                if child.pk in child_items:
                    child_items[child.pk].update(child)
                else:
                    item_child = MyItem(child)
                    self.addChild(item_child)

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        if column==0:
            return int(self.text(column)) < int(otherItem.text(column))
        else:
            return super(MyItem, self).__lt__(otherItem)
            
 #       if curve.has_childs:
 #           for child in curve.childs.all():
 #               child_item = 
 #               item_child = 
 #               MyItem(child)
 #               self.addChild(item_child)

class MyItemOld(QtGui.QTreeWidgetItem):
    def __init__(self, curve):
        super(MyItem, self).__init__([str(curve.id), curve.name, str(curve.date)])
        self.pk = curve.pk
        if curve.has_childs:
            for child in curve.childs.all():
                item_child = MyItem(child)
                self.addChild(item_child)

class MyTagInputDialog(QtGui.QDialog):
    def __init__(self):
        super(MyTagInputDialog, self).__init__()
        self.lay = QtGui.QVBoxLayout()
        self.label = QtGui.QLabel('Enter existing tag name:')
        self.line  = QtGui.QLineEdit()
        
        self.lay.addWidget(self.label)
        self.lay.addWidget(self.line)
        self.setLayout(self.lay)
        self.button_cancel = QtGui.QPushButton("Cancel")
        self.button_ok = QtGui.QPushButton("OK")
        self.hlay = QtGui.QHBoxLayout()
        self.lay.addLayout(self.hlay)
        self.hlay.addWidget(self.button_cancel)
        self.hlay.addWidget(self.button_ok)
        self.button_ok.clicked.connect(self.validate)
        self.button_cancel.clicked.connect(self.reject)
        self.line.setCompleter(TAG_COMPLETER)
    
    def validate(self):
        if str(self.line.text()) in [tag.name for tag in Tag.objects.all()]:
            self.accept()
    
    def ask_tag(self):
        ok = self.exec_()==1
        return self.line.text(), ok

class ListCurveWidget(QtGui.QWidget, object):
    current_item_changed = QtCore.pyqtSignal(object)
    refresh_clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent):
        super(ListCurveWidget, self).__init__(parent)
        self.popup = QtGui.QMessageBox()
        self.popup.setText('refreshing list, please wait.')
        self._tree_widget = self._get_tree_widget()
        self._lay = QtGui.QVBoxLayout()
        self.query_textbox = QtGui.QTextEdit()
        self.query_textbox.setMaximumHeight(60)
        self.query_textbox.setReadOnly(True)
        self._lay.addWidget(self.query_textbox)
        
        self._refresh_button = QtGui.QPushButton('refresh')
        self._refresh_button.clicked.connect(self.refresh)
        
        self._refresh_button.clicked.connect(self.refresh_clicked)
        self._lay_refresh = QtGui.QHBoxLayout()
        self._lay_refresh.addWidget(self._refresh_button)
        
        self._show_only_checkbox = QtGui.QCheckBox()
        self._show_only_checkbox.setCheckState(2)
        self._show_only_checkbox.stateChanged.connect(self.show_only_changed)
        self._lay_refresh.addWidget(self._show_only_checkbox)
        
        self._show_only_label = QtGui.QLabel('show first')
        self._lay_refresh.addWidget(self._show_only_label)
        
        self._show_only_spinbox = QtGui.QSpinBox()
        self._show_only_spinbox.setValue(25)
        self._show_only_spinbox.setMaximum(9999999)
        self._lay_refresh.addWidget(self._show_only_spinbox)
        
        self._show_only_total = QtGui.QLabel('/')
        self._lay_refresh.addWidget(self._show_only_total)
        
        self._lay.addLayout(self._lay_refresh)
        
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.addWidget(self._tree_widget)
#        self.refresh()
        self._tree_widget.itemSelectionChanged.connect(
                                          self._current_item_changed)
        self._refresh_button.pressed.connect(self.refresh_clicked)
        self._tree_widget.setSortingEnabled(True)
        self.setLayout(self._lay)
        self.setMinimumWidth(300)

    def set_total_label(self, val):
        self._show_only_total.setText('/' + str(val))

    @property
    def is_show_only(self):
        return self._show_only_checkbox.checkState()==2

    @is_show_only.setter
    def is_show_only(self, value):
        d = {2:True, 0:False}
        self._show_only_checkbox.setCheckState(d[value])
        
    def show_only_changed(self, check_state):
        widgets = [self._show_only_spinbox,
                   self._show_only_label,
                   self._show_only_total]
        for widget in widgets:
            widget.setEnabled(check_state==2)
        
    
    def _current_item_changed(self):
        if self.selected_curve:
            self.current_item_changed.emit(self.selected_curve)
    
    def select_by_id(self, id):
        """if the curve is in the list, selects it, otherwise cancels
        the current selection
        """
        for index in range(self._tree_widget.topLevelItemCount()):
            item = self._tree_widget.topLevelItem(index)
            if item.pk == id:
                #item.setSelected(True)
                self._tree_widget.setCurrentItem(item)
                return
#        self._tree_widget.clearSelection()
        
    @property
    def selected_curve(self):
        """
        Returns None if several or 0 curves are selected.
        """
        sel = self._tree_widget.selectedItems()
        if len(sel)!=1:
            return None
        else:
            try:
                curve = CurveDB.objects.get(pk = sel[0].pk)
            except CurveDB.DoesNotExist:
                return None
            else:
                return curve 

    @property
    def selected_curves(self):
        """
        Returns the list of selected curves
        """ 
        sel = self._tree_widget.selectedItems()
        curves = []
        for curve_item in sel:
            try:
                curve = CurveDB.objects.get(pk = curve_item.pk)
            except CurveDB.DoesNotExist:
                print "Didn't find curve id " + str(curve_item.pk) + " in the db"
            else:
                curves.append(curve)
        return curves
        
    def __contains__(self, curve):
        if not isinstance(curve, int):
            curve = curve.pk
        return curve in self.ids()
    
    def ids(self):
        return [self._tree_widget.topLevelItem(index).pk \
               for index in \
               range(self._tree_widget.topLevelItemCount())]
    
    def refresh_one_id(self, id):
        curves = self.parent().query()
        try:
            curve = curves.get(id=id)
        except CurveDB.DoesNotExist:
            return
        if curve.parent:
            return self.refresh_one_id(curve.parent.id)
        item_list = self._tree_widget.findItems(str(id),
                                               QtCore.Qt.MatchFlag(0),
                                               column=0)
        if item_list:
            item_list[0].update(curve)
        else:
            item = MyItem(curve)
            self._tree_widget.addTopLevelItem(item)
    
    def sort_field(self):
        d = {0:'id', 1:'_name', 2:'_date'}
        return d[self._tree_widget.sortColumn()]
    
    def sort_order(self):
        return self._tree_widget.header().sortIndicatorOrder()
    
    @property
    def num_display(self):
        return self._show_only_spinbox.value()
    
    def refresh(self):
        self.popup.show()
        curves = self.parent().query()
        query_string = self.parent().query_string()
        self.query_textbox.setText(query_string)
        
        if self.sort_order():# doesn't work when first doing order_by and then reverse!!! 
            curves = curves.filter(parent=None).order_by(self.sort_field()).reverse()
        else:
            curves = curves.filter(parent=None).order_by(self.sort_field())
        
        self._tree_widget.blockSignals(True)
        items = []
        total = curves.count()
        self.set_total_label(total)
        if self.is_show_only:
            sl = slice(0, self.num_display)
        else:
            sl = slice(0, total)
        
        for curve in curves[sl]:
            item_list = self._tree_widget.findItems(str(curve.id),
                                               QtCore.Qt.MatchFlag(0),
                                               column=0)
            if(item_list):
                item = item_list[0]
                item.update(curve)
            else:
                items.append(MyItem(curve))
                
        iterator = QtGui.QTreeWidgetItemIterator(self._tree_widget)
        item = iterator.value()
        root = self._tree_widget.invisibleRootItem() ##http://stackoverflow.com/questions/12134069/delete-qtreewidgetitem-in-pyqt 
        to_remove = []
        while(item):
            if item.ghost:
                to_remove.append(item)
            else:
                item.ghost = True
            iterator+=1
            item = iterator.value()
            
        for item in to_remove:
            (item.parent() or root).removeChild(item)
        #
        self._tree_widget.addTopLevelItems(items)
        for item in items:
            item.ghost = True
        self._tree_widget.blockSignals(False)
        self.popup.hide()
            
    def refresh_old(self):
        previous_id = None
        previous_selected = self._tree_widget.currentItem()
        if previous_selected:
            previous_id = previous_selected.pk
        curves = self.parent().query()
        curves = curves.filter(parent=None).order_by('id')
        self._tree_widget.blockSignals(True)
        self._tree_widget.clear()
        
        #for curve in curves:
        #    self.add_curve(curve)
        self._tree_widget.addTopLevelItems([MyItem(cu) for cu in curves])
        self._tree_widget.blockSignals(False)
        
        if not previous_id:
            return
        if previous_id in self:
            self.select_by_id(previous_id)
        else:
            dist = numpy.array(self.ids()) - previous_id
            if len(dist[dist>0]):
                next_id = min(dist[dist>0]) + previous_id
            else:
                if len(dist[dist<0]):
                    next_id = max(dist[dist<0]) + previous_id
                else:
                    return
            self.select_by_id(next_id)
    
    def _get_tree_widget(self):
        class ListTreeWidget(QtGui.QTreeWidget):
            def __init__(self, parent):
                super(ListTreeWidget, self).__init__(parent) 
                self.headerItem().setText(0, "curve id")                   
                self.headerItem().setText(1, "curve name")
                self.headerItem().setText(2, "curve date")
                self.setSortingEnabled(True)
                self.setSelectionMode( \
                            QtGui.QAbstractItemView.ExtendedSelection)
        return ListTreeWidget(self)


    
    def contextMenuEvent(self, event):
        """
        Context Menu (right click on the treeWidget)
        """
        curves = self.selected_curves
        ### First option: Plot curve(s)

        if len(curves)==1:
            message = "plot in " + curves[0].params['window']
            message_delete = "delete " + curves[0].name
            message_tags = "add a tag to selected curve"
            message_remove_tags = "remove a tag to selected curve"
        else:
            message = "plot these in their window"
            message_delete = "delete " + str(len(curves)) + " curves ?"
            message_tags = "add a tag to selected " + str(len(curves)) + " curves"
            message_remove_tags = "remove a tag to selected " +  str(len(curves)) + " curves"
        
        def delete(dummy, curves=curves):
            message_box = QtGui.QMessageBox(self)
            answer = message_box.question(self, 'delete', message_delete, 'No', 'Yes')
            if not answer:
                return
            for curve in curves:
                curve.delete()
            self.refresh()
        
        def plot(dummy, curves=curves):
            curves.reverse()
            for curve in curves:
                win = get_window(curve.params["window"])
                win.plot(curve)
                win.show()
        
        def create_csv(curves, buffer):
            df = pandas.DataFrame(dict([(str(curve.id) +\
                             '_' + curve.params["name"],
                              curve.data) for curve in curves]))
            df.to_csv(buffer, index_label='index')
            
        def export_clipboard(dummy, curves=curves):
            string = StringIO()
            create_csv(curves, string)
            clip = _APP.clipboard()
            clip.setText(string.getvalue())
                
                
        def export_csv(dummy, curves=curves):
            filename = str(QtGui.QFileDialog.getSaveFileName())
            with open(filename,'w') as f:
                create_csv(curves, f)
                
        def addtag(dummy,curves=curves):
            #text, ok = QtGui.QInputDialog.getText(self, 'Add a tag','Tagname to add:')
            text, ok = MyTagInputDialog().ask_tag()
            
            text = str(text)
            if ok:
                for curve in curves:
                    curve.tags.append(text)
                    curve.save()
        def removetag(dummy, curves=curves):
            text, ok = MyTagInputDialog().ask_tag()
            text = str(text)
            if ok:
                for curve in curves:
                    try:
                        curve.tags.remove(text)
                    except ValueError:
                        pass
                    else:
                        curve.save()
        
        menu = QtGui.QMenu(self)
        action_plot = QtGui.QAction(message, self)
        action_plot.triggered.connect(plot)
        
        action_delete = QtGui.QAction(message_delete, self)
        action_delete.triggered.connect(delete)

        action_tags = QtGui.QAction(message_tags, self)
        action_tags.triggered.connect(addtag)
        
        action_remove_tags = QtGui.QAction(message_remove_tags, self)
        action_remove_tags.triggered.connect(removetag)
        
        menu.addAction(action_plot)
        menu.addAction(action_delete)
        menu.addAction(action_tags)
        menu.addAction(action_remove_tags)
        
        
        ###second option: fit curve(s)
        
        fitfuncs = list()
        for f in dir(FitFunctions):
            if not f.startswith('_'):
                fitfuncs.append(f)
        
        fitsmenu = menu.addMenu('fits')
        gfitsmenu = menu.addMenu('manual fits')
        
        def fitcurve(curvestofit, funcname):
            for curve in curvestofit:
                curve.fit(func=funcname, autosave=True)
        def gfitcurve(curvestofit, funcname):
            for curve in curvestofit:
                curve.fit(func=funcname, autosave=True, graphicalfit=True)
                
        for f in fitfuncs:
            specificfit = functools.partial(fitcurve, curvestofit=curves, funcname=f)
            specificgfit = functools.partial(gfitcurve, curvestofit=curves, funcname=f)
            action_add_tag = QtGui.QAction(f, self)
            action_add_tag.triggered.connect(specificfit)
            action_gfit = QtGui.QAction(f, self)
            action_gfit.triggered.connect(specificgfit)
            fitsmenu.addAction(action_add_tag)
            gfitsmenu.addAction(action_gfit)


        exportmenu = menu.addMenu('export as csv')
        action_export_clipboard = QtGui.QAction('to clipboard', self)
        action_export_clipboard.triggered.connect(export_clipboard)
        action_export_csv = QtGui.QAction('to file ...', self)
        action_export_csv.triggered.connect(export_csv)
        exportmenu.addAction(action_export_clipboard)
        exportmenu.addAction(action_export_csv)
        
        
        def expand_selected():
            for item in self._tree_widget.selectedItems():
                self._tree_widget.expandItem(item)   
        def collapse_selected():
            for item in self._tree_widget.selectedItems():
                self._tree_widget.collapseItem(item)     
        expand_menu = menu.addMenu('expand')
        action_expand_all = QtGui.QAction('selected', self)
        action_expand_all.triggered.connect(expand_selected)
        expand_menu.addAction(action_expand_all)
        
        action_expand_all = QtGui.QAction('all', self)
        action_expand_all.triggered.connect(self._tree_widget.expandAll)
        expand_menu.addAction(action_expand_all)
        
        menu.addMenu(expand_menu)
        
        collapse_menu = menu.addMenu('collapse')
        action_collapse_all = QtGui.QAction('all', self)
        action_collapse_all.triggered.connect(self._tree_widget.collapseAll)
        
        action_collapse_selected = QtGui.QAction('selected', self)
        action_collapse_selected.triggered.connect(collapse_selected)
        collapse_menu.addAction(action_collapse_selected)
        
        collapse_menu.addAction(action_collapse_all)
        menu.addMenu(collapse_menu)
        
        menu.exec_(event.globalPos())
     
    