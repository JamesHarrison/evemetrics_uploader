#!/usr/bin/env python

import sys, os, time, traceback, pprint

from optparse import OptionParser
from cmdline import ParseWithFile

from evemetrics import parser, uploader
from evemetrics.file_watcher.generic import FileMonitor

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


class stdout_wrap( object ):
    def __init__( self, relay ):
        self.relay = relay

    def write( self, str ):
        self.relay( str )

class GUI( object ):
    def __init__( self, monitor, options, args ):
        self.monitor = monitor
        self.options = options
        self.args = args
        self.app = None
        self.status = None
        self.stdout_line = ''

        self.app = None
        self.mainwindow = None
        self.status = None
        self.watcher = None

        self.token_edit = None
        self.path_edit = None

    def setStatus( self, msg ):
        self.mainwindow.statusBar().showMessage( msg )        

    def monkeypatch_write( self, str ):
    	try:
    		sys.__stdout__.write( str )
    	except:
    	    ""
        # appendPlainText inserts \n for each call, compensate
        self.stdout_line += str
        spl = self.stdout_line.split('\n')
        if ( len( spl ) >= 2 ):
            while ( len( spl ) > 1 ):
                self.status.appendPlainText( spl[0] )
                spl = spl[1:]
            assert( len( spl ) == 1 )
            self.stdout_line = spl[0]

    def browsePath( self ):
        
        fileName = QtGui.QFileDialog.getExistingDirectory( self.mainwindow, 'Select your EvE directory (where eve.exe resides)' )
        
    def processCacheFile( path ):
        print "gogo"
        
    def Run( self ):
        self.app = QtGui.QApplication( self.args )

        if ( self.options.path ):
            #QtCore.QObject.connect(self.monitor, QtCore.SIGNAL("fileChanged(QString)"), self.processCacheFile)

            self.monitor.Run(self)
            
        # setup status log widget
        self.mainwindow = QtGui.QMainWindow()
        self.mainwindow.setWindowTitle( 'EvE Metrics uploader' )

        self.status = QtGui.QPlainTextEdit()
        self.status.setReadOnly( True )
        sys.stdout = stdout_wrap( self.monkeypatch_write )

        # tabs
        self.tabs = QtGui.QTabWidget()
        self.tabs.addTab( self.status, 'Activity' )

        prefs_layout = QtGui.QFormLayout()
        self.token_edit = QtGui.QLineEdit()
        prefs_layout.addRow( QtGui.QLabel( 'User Token:' ), self.token_edit )
        self.path_browse = QtGui.QPushButton( 'Change' )
        self.app.connect( self.path_browse, QtCore.SIGNAL( 'clicked()' ), self.browsePath )
        prefs_layout.addRow( QtGui.QLabel( 'EvE cache path:' ), self.path_browse )
        prefs_widg = QtGui.QWidget()
        prefs_widg.setLayout( prefs_layout )
        self.tabs.addTab( prefs_widg, 'Preferences' )

        if ( not self.options.token is None ):
            self.token_edit.setText( self.options.token )

        self.mainwindow.setCentralWidget( self.tabs )
        self.mainwindow.show()
        self.mainwindow.raise_()

        print 'Eve Metrics uploader started'

        sys.exit( self.app.exec_() )

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

    upload_client = uploader.Uploader()
    upload_client.set_token( options.token )
    processor = Processor( upload_client )
    qtAvailable = False

    if ( options.gui ):
        try:
            print 'Starting up GUI subsystem'
            from PyQt4 import QtCore
            from PyQt4 import QtGui
        except:
            traceback.print_exc()            
            print 'There was a problem with the PyQt backend. Running in text mode.'
        else:
            qtAvailable = True

    if (qtAvailable ):
        #from evemetrics.file_watcher.qt import QtFileMonitor
        from evemetrics.file_watcher.win32 import Win32FileMonitor
        monitor = Win32FileMonitor( processor )
        monitor.path = options.path
        gui = GUI( monitor, options, args )
        gui.Run()
    else:
        monitor = FileMonitor( processor )
        monitor.path = options.path
        monitor.Run( float( options.poll ) )

    if ( not options.gui and options.token is None or options.path is None ):
        raise Exception( 'Insufficient command line data' )

    
