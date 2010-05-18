import sys, os, time, traceback
import win32file
import win32con
import pywintypes
from PyQt4 import QtCore
from PyQt4.QtCore import QThread
import os; 
from .generic import FileMonitor

class Win32FileMonitor( FileMonitor ):
    def __init__( self, factory ):
        QThread.__init__(self, factory)
        self.exiting = False
        self.tree = None
        self.path = None
        self.valid_paths = []
        self.factory = factory
        self.last_run = time.time()
    def __del__(self):
        self.exiting = True
        self.wait()    
    # note: last modification time could work too, but I'm less trusting of the portability/reliability of that approach
    @classmethod
    def BaseCachePath( cls ):
        return os.environ['LOCALAPPDATA']  + "\\CCP\\\EVE\\"
    
    def Scan( self ):
        return None
    def Run( self, gui ):
        self.gui = gui
        self.path = gui.options.path
        if ( len(self.valid_paths) > 0 ):
            self.children = []
            for path in self.valid_paths:
                print "Monitoring: ", path
                monitor = Win32FileMonitor( self.processor, self )
                self.children.append( monitor )
                monitor.gui = gui
                monitor.path = path
                monitor.start()
                
        else:
            self.start()

    def run( self ):
        try:
            hDir = win32file.CreateFile (
                self.path,
                0x0001,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_FLAG_BACKUP_SEMANTICS,
                None
            )
        except pywintypes.error, e:
            print "Invalid cache file path: ", e
            return
    
        while not self.exiting:
            results = win32file.ReadDirectoryChangesW (
                hDir,
                1024,
                False,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None
            )
            for action, file in results:
                full_filename = os.path.join (self.path, file)
                if (action == 1 or action == 3):
                    print "got data ", action
                    self.factory.emit(QtCore.SIGNAL("fileChanged(QString)"), QtCore.QString(full_filename))

