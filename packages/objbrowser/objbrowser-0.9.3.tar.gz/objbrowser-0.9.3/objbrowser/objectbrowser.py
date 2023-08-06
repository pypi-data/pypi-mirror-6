""" 
    Object browser GUI in Qt
    
    #####################
    # TODO: version 1.0 #
    #####################
    
    # Installing
     - rename attribute_model.py to attributemodel.py
     - Pylint (google Pyside and Pylint)
     - Pip
     - Test under linux (table)
     - Python Package Index
     - sphynx
    
    
    #####################
    # TODO: version 1.x #
    #####################
    
    # Ordered dict don't sort keys 
    # hide non-attributes' attributes? That is, list's and dict's attributes are hidden.
    # tool-tips
    # python 3
    # Examples:
     - Qt
   
    Changes:
       # removed show_root_node parameter. Is implicit by testing obj_name == None
"""
from __future__ import absolute_import
from __future__ import print_function
import logging, traceback
from PySide import QtCore, QtGui
from PySide.QtCore import Qt

from objbrowser.version import PROGRAM_NAME, PROGRAM_VERSION, DEBUGGING
from objbrowser.treemodel import TreeModel
from objbrowser.attribute_model import DEFAULT_ATTR_COLS, DEFAULT_ATTR_DETAILS

logger = logging.getLogger(__name__)

        
# The main window inherits from a Qt class, therefore it has many 
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904, W0201 

class ObjectBrowser(QtGui.QMainWindow):
    """ Object browser main application window.
    """
    _n_instances = 0
    
    def __init__(self, obj,  
                 name = '',
                 attribute_columns = DEFAULT_ATTR_COLS,  
                 attribute_details = DEFAULT_ATTR_DETAILS,  
                 show_routine_attributes = None,
                 show_special_attributes = None, 
                 reset = False):
        """ Constructor
        
            :param obj: any Python object or variable
            :param name: name of the object as it will appear in the root node
            :param attribute_columns: list of AttributeColumn objects that define which columns
                are present in the table and their defaults
            :param attribute_details: list of AttributeDetails objects that define which attributes
                can be selected in the details pane.
            :param show_routine_attributes: if True rows where the 'is attribute' and 'is routine'
                columns are both True, are displayed. Otherwise they are hidden. 
            :param show_special_attributes: if True rows where the 'is attribute' is True and
                the object name starts and ends with two underscores, are displayed. Otherwise 
                they are hidden.
            :param reset: If true the persistent settings, such as column widths, are reset. 
        """
        super(ObjectBrowser, self).__init__()

        ObjectBrowser._n_instances += 1
        self._instance_nr = self._n_instances        
        
        # Model
        self._attr_cols = attribute_columns
        self._attr_details = attribute_details
        
        (show_routine_attributes, 
         show_special_attributes) = self._readModelSettings(show_routine_attributes = show_routine_attributes,
                                                            show_special_attributes = show_special_attributes)
        self._tree_model = TreeModel(obj, 
                                     root_obj_name = name,
                                     attr_cols = self._attr_cols,  
                                     show_routine_attributes = show_routine_attributes, 
                                     show_special_attributes = show_special_attributes)
        # Views
        self._setup_actions()
        self._setup_menu()
        self._setup_views()
        self.setWindowTitle("{} - {}".format(PROGRAM_NAME, name))
        app = QtGui.QApplication.instance()
        app.lastWindowClosed.connect(app.quit) 

        self._readViewSettings(reset = reset)
        
        # Update views with model
        self.toggle_special_attribute_action.setChecked(show_special_attributes)
        self.toggle_callable_action.setChecked(show_routine_attributes)
     
        # Select first row so that a hidden root node will not be selected.
        first_row = self._tree_model.first_item_index()
        self.obj_tree.setCurrentIndex(first_row)
            
            
    def _make_show_column_function(self, column_idx):
        """ Creates a function that shows or hides a column."""
        show_column = lambda checked: self.obj_tree.setColumnHidden(column_idx, not checked)
        return show_column            


    def _setup_actions(self):
        """ Creates the main window actions.
        """
        # Show/hide table column actions
        self.toggle_column_actions_group = QtGui.QActionGroup(self)
        self.toggle_column_actions_group.setExclusive(False)
        
        self.__toggle_functions = []  # for keeping references
        for col_idx, attr_col in enumerate(self._attr_cols):
            action = QtGui.QAction("Show {} column".format(attr_col.name), 
                                   self.toggle_column_actions_group, checkable=True, checked=True,
                                   statusTip = "Shows or hides the {} column".format(attr_col.name))
                
            if col_idx >= 0 and col_idx <= 9:
                action.setShortcut("Ctrl+{:d}".format(col_idx))
                
            func = self._make_show_column_function(col_idx) 
            self.__toggle_functions.append(func) # keep reference
            assert action.toggled.connect(func)
            
        # Show/hide callable objects
        self.toggle_callable_action = \
            QtGui.QAction("Show routine attributes", self, checkable=True, 
                          statusTip = "Shows/hides attributes that are routings (functions, methods, etc)")
        assert self.toggle_callable_action.toggled.connect(self.toggle_callables)
                              
        # Show/hide special attributes
        self.toggle_special_attribute_action = \
            QtGui.QAction("Show __special__ attributes", self, checkable=True, 
                          statusTip = "Shows or hides __special__ attributes")
        assert self.toggle_special_attribute_action.toggled.connect(self.toggle_special_attributes)
                              
                              
    def _setup_menu(self):
        """ Sets up the main menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("C&lose", self.close_window, "Ctrl+W")
        file_menu.addAction("E&xit", self.quit_application, "Ctrl+Q")
        if DEBUGGING is True:
            file_menu.addSeparator()
            file_menu.addAction("&Test", self.my_test, "Ctrl+T")
        
        view_menu = self.menuBar().addMenu("&View")
        show_cols_submenu = view_menu.addMenu("Table columns")
        for action in self.toggle_column_actions_group.actions():
            show_cols_submenu.addAction(action)
        view_menu.addSeparator()
        view_menu.addAction(self.toggle_callable_action)
        view_menu.addAction(self.toggle_special_attribute_action)
        
        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About', self.about)


    def _setup_views(self):
        """ Creates the UI widgets. 
        """
        self.central_splitter = QtGui.QSplitter(self, orientation = QtCore.Qt.Vertical)
        self.setCentralWidget(self.central_splitter)
        central_layout = QtGui.QVBoxLayout()
        self.central_splitter.setLayout(central_layout)
        
        # Tree widget
        self.obj_tree = QtGui.QTreeView()
        self.obj_tree.setAlternatingRowColors(True)
        self.obj_tree.setModel(self._tree_model)
        self.obj_tree.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.obj_tree.setUniformRowHeights(True)
        self.obj_tree.setAnimated(True)
        
        # Stretch last column? 
        # It doesn't play nice when columns are hidden and then shown again.
        obj_tree_header = self.obj_tree.header()
        obj_tree_header.setStretchLastSection(False)
        #obj_tree_header.setResizeMode(0, QtGui.QHeaderView.Stretch) # doesn't work smoothly
        obj_tree_header.setContextMenuPolicy(Qt.ActionsContextMenu)
        for action in self.toggle_column_actions_group.actions():
            obj_tree_header.addAction(action)

        central_layout.addWidget(self.obj_tree)

        # Bottom pane
        bottom_pane_widget = QtGui.QWidget()
        bottom_layout = QtGui.QHBoxLayout()
        bottom_layout.setSpacing(0)
        bottom_layout.setContentsMargins(5, 5, 5, 5) # left top right bottom
        bottom_pane_widget.setLayout(bottom_layout)
        central_layout.addWidget(bottom_pane_widget)
        
        group_box = QtGui.QGroupBox("Details")
        bottom_layout.addWidget(group_box)
        
        group_layout = QtGui.QHBoxLayout()
        group_layout.setContentsMargins(2, 2, 2, 2) # left top right bottom
        group_box.setLayout(group_layout)
        
        # Radio buttons
        radio_widget = QtGui.QWidget()
        radio_layout = QtGui.QVBoxLayout()
        radio_layout.setContentsMargins(0, 0, 0, 0) # left top right bottom        
        radio_widget.setLayout(radio_layout) 

        self.button_group = QtGui.QButtonGroup(self)
        for button_id, attr_detail in enumerate(self._attr_details):
            radio_button = QtGui.QRadioButton(attr_detail.name)
            radio_layout.addWidget(radio_button)
            self.button_group.addButton(radio_button, button_id)

        self.button_group.buttonClicked[int].connect(self._change_details_field)
        self.button_group.button(0).setChecked(True)
                
        radio_layout.addStretch(1)
        group_layout.addWidget(radio_widget)

        # Editor widget
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(14)

        self.editor = QtGui.QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setFont(font)
        group_layout.addWidget(self.editor)
        
        # Splitter parameters
        self.central_splitter.setCollapsible(0, False)
        self.central_splitter.setCollapsible(1, True)
        self.central_splitter.setSizes([400, 200])
        self.central_splitter.setStretchFactor(0, 10)
        self.central_splitter.setStretchFactor(1, 0)
               
        # Connect signals
        selection_model = self.obj_tree.selectionModel()
        assert selection_model.currentChanged.connect(self._update_details)

    # End of setup_methods
    
    def _readModelSettings(self, 
                           show_routine_attributes = None,
                           show_special_attributes = None):
        """ Reads the persistent model settings
        """ 
        logger.debug("Reading model settings for window: {:d}".format(self._instance_nr))
        
        settings = QtCore.QSettings()
        settings.beginGroup("model_{:d}".format(self._instance_nr))
        if show_routine_attributes is None:
            show_routine_attributes = settings.value("show_routine_attributes", True)
        if show_special_attributes is None:
            show_special_attributes = settings.value("show_special_attributes", True)
        settings.endGroup()
        return (show_routine_attributes, show_special_attributes)
                    
    
    def _writeModelSettings(self):
        """ Writes the model settings to the persistent store
        """         
        logger.debug("Writing model settings for window: {:d}".format(self._instance_nr))
        
        settings = QtCore.QSettings()
        settings.beginGroup("model_{:d}".format(self._instance_nr))
        settings.setValue("show_routine_attributes", self._tree_model.getShowCallables())
        settings.setValue("show_special_attributes", self._tree_model.getShowSpecialAttributes())
        settings.endGroup()
            
            
    def _readViewSettings(self, reset=False):
        """ Reads the persistent program settings
        
            :param reset: If True, the program resets to its default settings
        """ 
        logger.debug("Reading view settings for window: {:d}".format(self._instance_nr))
        
        pos = QtCore.QPoint(20 * self._instance_nr, 20 * self._instance_nr)
        window_size = QtCore.QSize(1024, 700)
        details_button_idx = 0
        column_sizes = [col.width for col in self._attr_cols]
        column_visible = [col.col_visible for col in self._attr_cols]
        
        if not reset:
            settings = QtCore.QSettings()
            settings.beginGroup("view_{:d}".format(self._instance_nr))
            pos = settings.value("main_window/pos", pos)
            window_size = settings.value("main_window/size", window_size)
            details_button_idx = settings.value("details_button_idx", details_button_idx)
            self.central_splitter.restoreState(settings.value("central_splitter/state"))
            
            for idx, attr_col in enumerate(self._attr_cols):
                key = "table_col/{}/width".format(attr_col.settings_name)
                column_sizes[idx] = settings.value(key, column_sizes[idx])
                key = "table_col/{}/col_visible".format(attr_col.settings_name)
                column_visible[idx] = settings.value(key, column_visible[idx])
                
            settings.endGroup()
            
        self.resize(window_size)
        self.move(pos)
        button = self.button_group.button(details_button_idx)
        if button is not None:
            button.setChecked(True)

        header = self.obj_tree.header()
        for idx, size in enumerate(column_sizes):
            if size > 0: # Just in case 
                header.resizeSection(idx, size)

        for idx, visible in enumerate(column_visible):
            self.toggle_column_actions_group.actions()[idx].setChecked(visible)                


    def _writeViewSettings(self):
        """ Writes the view settings to the persistent store
        """         
        logger.debug("Writing view settings for window: {:d}".format(self._instance_nr))
        
        settings = QtCore.QSettings()
        settings.beginGroup("view_{:d}".format(self._instance_nr))
        
        # We cannot use QHeaderView.restoreState or QSettings.beginReadArray because the
        # header does not always contain the same columns, so we store the by name.
        header = self.obj_tree.header()
        for idx in range(header.count()):
            key = "table_col/{}/col_visible".format(self._attr_cols[idx].settings_name)
            visible = not header.isSectionHidden(idx)
            settings.setValue(key, visible)
            if visible: # only save col_visible columns.
                column_size = header.sectionSize(idx)
                assert (column_size > 0), "Sanity check: column_size: {}".format(column_size) 
                key = "table_col/{}/width".format(self._attr_cols[idx].settings_name)
                settings.setValue(key, column_size)
                
            
        settings.setValue("central_splitter/state", self.central_splitter.saveState())
        settings.setValue("details_button_idx", self.button_group.checkedId())
        settings.setValue("main_window/pos", self.pos())
        settings.setValue("main_window/size", self.size())
        settings.endGroup()
            

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def _update_details(self, current_index, _previous_index):
        """ Shows the object details in the editor given an index.
        """
        tree_item = self._tree_model.treeItem(current_index)
        self._update_details_for_item(tree_item)

        
    def _change_details_field(self, _button_id=None):
        """ Changes the field that is displayed in the details pane
        """
        #logger.debug("_change_details_field: {}".format(_button_id))
        current_index = self.obj_tree.selectionModel().currentIndex()
        tree_item = self._tree_model.treeItem(current_index)
        self._update_details_for_item(tree_item)
        
            
    def _update_details_for_item(self, tree_item):
        """ Shows the object details in the editor given an tree_item
        """
        self.editor.setStyleSheet("color: black;")
        try:
            #obj = tree_item.obj
            button_id = self.button_group.checkedId()
            assert button_id >= 0, "No radio button selected. Please report this bug."
            attr_details = self._attr_details[button_id]
            data = attr_details.data_fn(tree_item)
            self.editor.setPlainText(data)
            self.editor.setWordWrapMode(attr_details.line_wrap)
            
        except StandardError, ex:
            self.editor.setStyleSheet("color: red;")
            stack_trace = traceback.format_exc()
            self.editor.setPlainText("{}\n\n{}".format(ex, stack_trace))
            self.editor.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
            if DEBUGGING is True:
                raise

    
    def toggle_callables(self, checked):
        """ Shows/hides the special callable objects.
            Callable objects are functions, methods, etc. They have a __call__ attribute. 
        """
        logger.debug("toggle_callables: {}".format(checked))
        self._tree_model.setShowCallables(checked)
        if self._tree_model.show_root_node:
            self.obj_tree.expandToDepth(0)        

    def toggle_special_attributes(self, checked):
        """ Shows/hides the special attributes.
            Special attributes are objects that have names that start and end with two underscores.
        """
        logger.debug("toggle_special_attributes: {}".format(checked))
        self._tree_model.setShowSpecialAttributes(checked)
        if self._tree_model.show_root_node:
            self.obj_tree.expandToDepth(0)


    def my_test(self):
        """ Function for testing """
        logger.debug("my_test")
        
    def about(self):
        """ Shows the about message window. """
        message = u"{} version {}""".format(PROGRAM_NAME, PROGRAM_VERSION)
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, message)

    def close_window(self):
        """ Closes the window """
        self.close()
        
    def quit_application(self):
        """ Closes all windows """
        app = QtGui.QApplication.instance()
        app.closeAllWindows()

    def closeEvent(self, event):
        """ Close all windows (e.g. the L0 window).
        """
        logger.debug("closeEvent")
        self._writeModelSettings()                
        self._writeViewSettings()                
        self.close()
        event.accept()
            

