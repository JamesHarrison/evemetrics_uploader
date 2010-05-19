import sys, os, time, traceback, platform

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import QThread

class FileMonitor( QThread ):
    def __init__( self, factory, path ):
        QThread.__init__( self )
        self.factory = factory
        self.path = path
        self.exiting = False
        self.tree = None

    # note: last modification time could work too, but I'm less trusting of the portability/reliability of that approach
    def Scan( self ):
        if ( self.path is None ):
            print 'Path is not defined'
            return
        tree = set()
        for root, dirs, files in os.walk( self.path ):
            for fi in files:
                fn = os.path.join( self.path, root, fi )
                # skip != .cache early to minimize work
                if ( os.path.splitext( fn )[1] != '.cache' ):
                    continue
                tree.add( ( fn, os.stat( fn ).st_mtime ) )
        if ( self.tree is None ):
            self.tree = tree
            return
        # see what new files may have been added
        new = tree.difference( self.tree )
        if ( len( new ) != 0 ):
#            pprint.pprint( new )
            for fn in new:
                fpn = os.path.join( self.path, fn[0] )
#                pprint.pprint( fpn )
                self.factory.emit(QtCore.SIGNAL("fileChanged(QString)"), QtCore.QString(fpn))
        self.tree = tree
        print '%d files' % len( self.tree )

    # this is our code asking the threads to start
    def Run( self ):
        self.start()

    def __del__( self ):
        self.exiting = True
        self.wait()

    # this is the thread's execution loop
    def run( self ):
        self.Scan() # prime the tree
        while not self.exiting:
            # FIXME: expose the options and wait the right amount of time
            time.sleep( 30 )
            self.Scan()
