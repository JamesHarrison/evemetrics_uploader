import sys, os, time, traceback, errno, logging

from PyQt4 import QtCore
from PyQt4.QtCore import QThread

import pyinotify

from .generic import FileMonitor

class EventHandler( pyinotify.ProcessEvent ):
    def __init__( self, factory ):
        self.factory = factory
        
    def process_IN_CREATE( self, event ):
        self.factory.emit( QtCore.SIGNAL( "fileChanged(QString)" ), QtCore.QString( event.pathname ) )

    def process_IN_MODIFY( self, event ):
        self.factory.emit( QtCore.SIGNAL( "fileChanged(QString)" ), QtCore.QString( event.pathname ) )

class PosixFileMonitor( QThread ):

    def __init__( self, factory, path, options ):
        QThread.__init__( self )
        self.exiting = False
        self.path = path
        self.factory = factory

        self.handler = EventHandler( factory )
        pyinotify.VERBOSE = True
        self.wm = pyinotify.WatchManager()
        self.notifier = pyinotify.Notifier( self.wm, self.handler )
        ret = self.wm.add_watch( self.path, pyinotify.IN_MODIFY | pyinotify.IN_CREATE, rec = False )
        if ( len( ret ) == 0 or ret[ self.path ] == -1 ):
            raise Exception( 'add_watch failed' )
        self.wdd = ret

    def __del__(self):
        self.exiting = True
        self.wait()    

    # this is our code asking the threads to start
    def Run( self ):
        # start the thread
        self.start()

    # this is the thread's execution loop
    def run( self ):
        while not self.exiting:
            self.notifier.loop()
