import sys, os, time, traceback, platform

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from .generic import FileMonitor

class MonitorFactory( QThread ):
    
    def __init__( self, monitorClass ):
        QThread.__init__(self, None)
        self.valid_paths = []
        self.monitorClass = monitorClass
        self.GuessCachePaths( self.monitorClass.BaseCachePath() )
        self.children = []

    def GuessCachePaths( self, baseCachePath ):
        print baseCachePath
        for installation in os.listdir(baseCachePath):
            ndir = os.path.join(baseCachePath,installation) + "\cache\MachoNet\87.237.38.200"
            try:
                for machnonet_version in os.listdir(ndir):
                    if ( int(machnonet_version) >= 235 ):
                        self.valid_paths.append( os.path.join( os.path.join(ndir, machnonet_version), "CachedMethodCalls" ) )
            except OSError, e:
                pass
    
    def Scan( self ):
        return None
    
    def Run( self, gui ):
        self.gui = gui
        self.path = gui.options.path
        if ( len(self.valid_paths) > 0 ):
            for path in self.valid_paths:
                print "Monitoring: ", path
                monitor = self.monitorClass( self )
                self.children.append( monitor )
                monitor.path = path
                monitor.Run()
