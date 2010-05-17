import sys, os, time, traceback

class FileMonitor( object ):
    def __init__( self, processor ):
        self.processor = processor
        self.tree = None
        self.path = None
        self.last_run = time.time()
        
    # note: last modification time could work too, but I'm less trusting of the portability/reliability of that approach
    def Scan( self ):
        # QFileSystemWatcher is emitting three signals in a row, we need to throttle a bit ...
        if ( time.time() - self.last_run  < 1 ):
            return
        self.last_run = time.time()
        
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
                self.processor.OnNewFile( fpn )
        self.tree = tree
        print '%d files' % len( self.tree )

    def Run( self, poll ):
        # first call is a no-op initializing the list
        self.Scan()
        while ( True ):
            try:
                self.Scan()
            except:
                traceback.print_exc()
            time.sleep( poll )
