# -*- coding: utf-8 -*-
import template
from PyQt4 import QtCore, QtGui
from acq4.util.HelpfulException import HelpfulException
from acq4.Manager import logMsg, logExc, getManager


class FileLoader(QtGui.QWidget):
    """Interface for 1) displaying directory tree and 2) loading a file from the tree.
    You must call setHost, and the widget will call host.loadFileRequested whenever 
    the user requests to load a file."""
    
    
    sigFileLoaded = QtCore.Signal(object)
    sigBaseChanged = QtCore.Signal(object)
    sigSelectedFileChanged = QtCore.Signal(object)
    
    def __init__(self, dataManager, host=None, showFileTree=True):
        self._baseDir = None
        self.dataManager = dataManager
        self.loaded = []
        QtGui.QWidget.__init__(self)
        self.ui = template.Ui_Form()
        self.ui.setupUi(self)
        self.setHost(host)
        
        self.ui.setDirBtn.clicked.connect(self.setBaseClicked)
        self.ui.loadBtn.clicked.connect(self.loadClicked)
        self.ui.dirTree.currentItemChanged.connect(self.updateNotes) ## self.ui.dirTree is a DirTreeWidget
        self.ui.dirTree.itemDoubleClicked.connect(self.doubleClickEvent)
        self.ui.fileTree.currentItemChanged.connect(self.selectedFileChanged)
        
        self.ui.fileTree.setVisible(showFileTree)
        self.ui.notesTextEdit.setReadOnly(True)
        self.setBaseClicked()
        
        
    def setHost(self, host):
        self.host = host
        
    def setBaseClicked(self):
        dh = self.dataManager.selectedFile()
        if dh is None:
            dh = getManager().getBaseDir()
        if dh is None:
            return
            #logMsg("Cannot set base directory because no directory is selected in Data Manager.", msgType='error')
            #return
        if not dh.isDir():
            dh = dh.parent()

        self.ui.dirTree.setBaseDirHandle(dh)
        self._baseDir = dh
        self.sigBaseChanged.emit(dh)
        
    def baseDir(self):
        return self._baseDir
        
    def loadClicked(self):
        fh = self.ui.dirTree.selectedFiles()
        self.loadFile(fh)
        
    def doubleClickEvent(self, item, column):
        fh = self.ui.dirTree.handle(item)
        self.loadFile([fh])
        
    def loadFile(self, files):
        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            for fh in files:
                if self.host is None:
                    self.sigFileLoaded.emit(fh)
                    self.loaded.append(fh)
                elif self.host.loadFileRequested([fh]):
                    name = fh.name(relativeTo=self.ui.dirTree.baseDirHandle())
                    item = QtGui.QTreeWidgetItem([name])
                    item.file = fh
                    self.ui.fileTree.addTopLevelItem(item)
                    self.sigFileLoaded.emit(fh)
                    self.loaded.append(fh)
            #self.emit(QtCore.SIGNAL('fileLoaded'), fh)
        finally:
            QtGui.QApplication.restoreOverrideCursor()
            
    def selectedFileChanged(self):
        self.sigSelectedFileChanged.emit(self.ui.fileTree.currentItem())
        
    def addVirtualFiles(self, itemNames, parentName=None):
        """Add names in itemNames to the list of loaded files. If parentName is specified items will be added as children of the parent."""
        for name in itemNames:
            item = QtGui.QTreeWidgetItem([name])
            if parentName is not None:
                parent = self.ui.fileTree.findItems(parentName, QtCore.Qt.MatchExactly)[0]
                parent.addChild(item)
            else:
                self.ui.fileTree.addTopLevelItem(item)
        
    def selectedFile(self):
        """Returns the file selected from the list of already loaded files"""
        item = self.ui.fileTree.currentItem()
        if item is None:
            return None
        return item.file
        
    def selectedFiles(self):
        """Returns the files selected in the file tree."""
        return self.ui.dirTree.selectedFiles()

        
    def updateNotes(self, current, previous):
        #sFile = self.ui.dirTree.selectedFile()
        fh = current
        if fh is None:
            return
        
        notes = fh.handle.info().get('notes', ' ')
        
        self.ui.notesTextEdit.setPlainText(notes)
        #print fh
        #print fh.info()
        
    def loadedFiles(self):
        """Return a list of loaded file handles"""
        return self.loaded[:]
        