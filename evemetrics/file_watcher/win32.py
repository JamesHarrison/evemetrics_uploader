import sys, os, time, traceback
import win32file
import win32con
from PyQt4 import QtCore
from PyQt4.QtCore import QThread

class Win32FileMonitor( QThread ):
    def __init__( self, processor, parent = None ):
        
        QThread.__init__(self, parent)
        self.exiting = False
        self.processor = processor
        self.tree = None
        self.path = None
        self.last_run = time.time()
    def __del__(self):
        self.exiting = True
        self.wait()    
    # note: last modification time could work too, but I'm less trusting of the portability/reliability of that approach
    def Scan( self ):
        return None
    def Run( self, gui, path ):
        self.gui = gui
        self.path = path
        self.start()

    def run( self ):
        hDir = win32file.CreateFile (
            self.path,
            0x0001,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,
            None
        )

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
                    self.emit(QtCore.SIGNAL("fileChanged(QString)"), QtCore.QString(full_filename))

