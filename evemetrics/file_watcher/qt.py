from PyQt4 import QtCore
from PyQt4 import QtGui
import sys, os, time
from .generic import FileMonitor

class QtFileMonitor( FileMonitor ):
    def Run( self, gui ):
        # just poll when the directory changed
        self.watcher = QtCore.QFileSystemWatcher(gui.mainwindow)
        self.watcher.addPath(gui.options.path)
        QtCore.QObject.connect(self.watcher,QtCore.SIGNAL("directoryChanged(const QString&)"), self.Scan)

