import sys, os, time, traceback
from PyQt4 import QtCore
from PyQt4.QtCore import QThread
import pyinotify

class EventHandler(pyinotify.ProcessEvent):
    def __init__( self, monitor):
        self.monitor = monitor
        
    def process_IN_CREATE(self, event):
        self.monitor.emit(QtCore.SIGNAL("fileChanged(QString)"), QtCore.QString(event.pathname))
    def process_IN_MODIFY(self, event):
        self.monitor.emit(QtCore.SIGNAL("fileChanged(QString)"), QtCore.QString(event.pathname))

class PosixFileMonitor( QThread ):
    def __init__( self, processor, parent = None ):
        QThread.__init__(self, parent)
        self.exiting = False
        self.processor = processor
        self.path = None
        self.last_run = time.time()
        self.handler = EventHandler(self)
        
        self.wm = pyinotify.WatchManager()
        self.notifier = pyinotify.Notifier(self.wm, self.handler)

    def __del__(self):
        self.exiting = True
        self.wait()    
    # note: last modification time could work too, but I'm less trusting of the portability/reliability of that approach
    def Scan( self ):
        return None
    def Run( self, gui, path ):
        self.gui = gui
        self.path = path
        self.wdd = self.wm.add_watch(self.path, pyinotify.IN_MODIFY | pyinotify.IN_CREATE, rec=True)

        self.start()

    def run( self ):
        while not self.exiting:
            self.notifier.loop()
