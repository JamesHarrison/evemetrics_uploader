import sys, os, time, traceback, errno, logging

import pyinotify

from .generic import FileMonitor

class EventHandler( pyinotify.ProcessEvent ):
    def __init__( self, factory ):
        self.factory = factory
        
    def process_IN_CREATE( self, event ):
        self.factory.processor.OnNewFile(event.pathname)

    def process_IN_MODIFY( self, event ):
        self.factory.processor.OnNewFile(event.pathname)

class PosixFileMonitor( Thread ):

    def __init__( self, factory, path, options ):
        Thread.__init__( self )
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
