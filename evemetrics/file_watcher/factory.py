import sys, os, time, traceback, platform

from .generic import FileMonitor
from threading import Thread
import logging
class MonitorFactory( Thread ):
    
    def __init__( self, monitorClass, valid_paths, options ):
        Thread.__init__( self )
        self.processor = None
        self.valid_paths = valid_paths
        self.monitorClass = monitorClass
        self.children = []

        for path in self.valid_paths:
            # the children emit signals to this factor to communicate back changes
            self.children.append( self.monitorClass( self, path, options ) )

    def Run( self ):
        for child in self.children:
            child.Run()

    def setProcessor( self, processor ):
        self.processor = processor
        # NOTE: since the children are each their own thread, are we risking re-entrant calls into the processing?
        # signal_established = QtCore.QObject.connect( self, QtCore.SIGNAL( "fileChanged(QString)" ), processor.OnNewFile )
        # assert( signal_established )
