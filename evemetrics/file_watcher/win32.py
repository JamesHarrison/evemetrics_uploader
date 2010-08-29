import sys, os, traceback
import win32file
import win32con
import win32event
import win32api
import pywintypes
import os; 
from .generic import FileMonitor
from threading import Thread
import logging

logger = logging.getLogger('emu')

class Win32FileMonitor( FileMonitor ):

    def __init__( self, factory, path, options ):
        Thread.__init__(self)
        self.exiting = False
        self.tree = None
        self.path = path
        self.factory = factory
        self.buffer = win32file.AllocateReadBuffer(8192)
        self.overlapped = pywintypes.OVERLAPPED()
        # As per docs for GetOverlappedResult, we muse use a manual reset event.
        self.overlapped.hEvent = win32event.CreateEvent(None, True, 0, None)
        self.overlapped.object = path
        
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def __del__(self):
        self.exiting = True
        win32event.SetEvent(self.stop_event)

    def Run( self ):
        self.start()

    def _async_watch( self ):
      win32file.ReadDirectoryChangesW (
        self.hDir,
        self.buffer,
        False,
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
        self.overlapped,
      )
    def run( self ):
        try:
            self.hDir = win32file.CreateFile (
                self.path,
                0x0001,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_FLAG_BACKUP_SEMANTICS | win32file.FILE_FLAG_OVERLAPPED,
                None
            )
            
        except pywintypes.error, e:
            logger.error("Invalid cache file path: %s" % e)
            return
        try:
          self._async_watch()
        except win32file.error, exc:
            logger.error("Failed to read directory changes for '%s'" % self.path)

        while not self.exiting:
            rc = win32event.WaitForMultipleObjects([self.stop_event,self.overlapped.hEvent], False, 1000)
            if rc == win32event.WAIT_TIMEOUT:
              # timeouts happen, we ignore them
              continue
            if rc == win32event.WAIT_OBJECT_0:
              # stop the thread.
              self.exiting = True
              break
            win32event.ResetEvent(self.overlapped.hEvent)
            try:
                bytes = win32file.GetOverlappedResult(self.hDir, self.overlapped, True)
            except win32file.error, exc:
                logger.warning("Failed to get directory changes for '%s':\n %s" % (self.path, exc))
                continue

            results = win32file.FILE_NOTIFY_INFORMATION(self.buffer, bytes)

            for action, file in results:
                full_filename = os.path.join (self.path, file)
                logger.debug("FileChanged: %s %s" % (action, file))
                #print "ACTION------------------> %s" % action
                if (action == 3):
                  self._async_watch()
                  self.factory.queue( (5,full_filename) )
