import sys, os, time, traceback
import win32file
import win32con
import pywintypes
import os; 
from .generic import FileMonitor
from threading import Thread
import logging

class Win32FileMonitor( FileMonitor ):

    def __init__( self, factory, path, options ):
        Thread.__init__(self)
        self.exiting = False
        self.tree = None
        self.path = path
        self.factory = factory
        self.last_run = time.time()

    def __del__(self):
        self.exiting = True
        #self.wait()    
    
    def Run( self ):
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
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
                None,
                None
            )
            for action, file in results:
                full_filename = os.path.join (self.path, file)
                logging.debug("FileChanged: %s %s" % (action, file))
                #print "ACTION------------------> %s" % action
                if (action == 3):
                  self.factory.processor.OnNewFile(full_filename)

