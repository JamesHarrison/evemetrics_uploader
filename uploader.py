#!/usr/bin/env python

import sys, os, time, traceback, pprint

from optparse import OptionParser
from cmdline import ParseWithFile

from evemetrics import parser, uploader

class Processor( object ):
    def __init__( self, upload_client ):
        self.upload_client = upload_client

    def OnNewFile( self, pathname ):
        try:
            print 'New or modified file: %s' % pathname
            if ( os.path.splitext( pathname )[1] != '.cache' ):
                print 'Not .cache, skipping'
                return
            try:
                parsed_data = parser.parse( pathname )
            except IOError:
                # I was retrying initially, but some files are deleted before we get a chance to parse them,
                # which is what's really causing this
                print 'IOError exception, skipping'
                return
            if ( parsed_data is None ):
                print 'No data parsed'
                return
            print 'Call %s, regionID %d, typeID %d' % ( parsed_data[0], parsed_data[1], parsed_data[2] )
            ret = self.upload_client.send(parsed_data)
        except:
            traceback.print_exc()
        else:
            print ret

class PollMonitor( object ):
    def __init__( self, processor ):
        self.processor = processor
        self.tree = None

    # note: last modification time could work too, but I'm less trusting of the portability/reliability of that approach
    def Scan( self, path ):
        tree = set()
        for root, dirs, files in os.walk( path ):
            for fi in files:
                fn = os.path.join( path, root, fi )
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
                fpn = os.path.join( path, fn[0] )
#                pprint.pprint( fpn )
                self.processor.OnNewFile( fpn )
        self.tree = tree
        print '%d files' % len( self.tree )

    def Run( self, poll, path ):
        # first call is a no-op initializing the list
        self.Scan( path )
        while ( True ):
            try:
                self.Scan( path )
            except:
                traceback.print_exc()
            time.sleep( poll )

if ( __name__ == '__main__' ):
    # using cmdline helper module for disk backing
    # pydoc ./cmdline.py
    # defaults are handled separately with the cmdline module
    defaults = { 'poll' : 10, 'gui' : True }
    p = OptionParser()
    # core
    p.add_option( '-t', '--token', dest = 'token', help = 'EVE Metrics uploader token - see http://www.eve-metrics.com/downloads' )
    p.add_option( '-p', '--path', dest = 'path', help = 'EVE cache path' )
    # UI
    p.add_option( '-n', '--nogui', action = 'store_false', dest = 'gui', help = 'Run in text mode' )
    p.add_option( '-g', '--gui', action = 'store_true', dest = 'gui', help = 'Run in GUI mode' )
    # filesystem alteration monitoring
    p.add_option( '-P', '--poll', dest = 'poll', help = 'Poll every n seconds (default %d)' % defaults['poll'] )

    ( options, args ) = ParseWithFile( p, defaults, filename = 'eve_uploader.ini' )

    print 'Token: %r' % options.token
    print 'Path: %r' % options.path
    print 'GUI: %r' % options.gui

    if ( options.gui ):
        print 'GUI mode not supported yet.'

    # TODO: if gui mode, initialize pyqt modules etc.
    # TODO: auto detect path if needed
    # TODO: prompt for token and path (GUI)

    upload_client = uploader.Uploader()
    upload_client.set_token( options.token )
    processor = Processor( upload_client )
    monitor = PollMonitor( processor )
    monitor.Run( float( options.poll ), options.path )
