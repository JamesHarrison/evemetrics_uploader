import sys, os, time, traceback, platform

from threading import Thread

class FileMonitor( Thread ):
    def __init__( self, factory, path, config ):
        Thread.__init__( self )
        self.factory = factory
        self.path = path
        self.config = config
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
            for fn in new:
                fpn = os.path.join( self.path, fn[0] )
                self.factory.queue( (5, fpn) )
        self.tree = tree

    # this is the thread's entry point
    def run( self ):
        self.Scan() # prime the tree
        while ( True ):
            time.sleep( self.config.options.poll )
            self.Scan()

    # this is our code asking the threads to start
    def Run( self ):
        self.start()
        
    def __del__( self ):
        self.exiting = True
