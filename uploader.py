#!/usr/bin/env python

import sys, os, time, traceback, pprint

from optparse import OptionParser
from cmdline import ParseWithFile

from evemetrics import parser, uploader

from evemetrics.file_watcher.generic import FileMonitor
from evemetrics.file_watcher.factory import MonitorFactory

class Processor( object ):
    def __init__( self, upload_client ):
        self.upload_client = upload_client

    def OnNewFile( self, pathname ):
        try:
            if ( pathname.__class__ == QtCore.QString ):
                pathname = str(pathname)
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
        
class Uploader ( object ):
    def __init__( self, monitor, processor, options, args ):
        self.monitor = monitor
        self.processor = processor
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

    def processCacheFile( self, fileName ):
        self.processor.OnNewFile(str(fileName))

class Console ( Uploader ):
    def Run( self ):
        import signal
        self.app = QtCore.QCoreApplication(args)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        QtCore.QObject.connect(self.monitor, QtCore.SIGNAL("fileChanged(QString)"), self.processor.OnNewFile )
        self.monitor.Run( self )
        self.app.exec_()

    
class GUI( Uploader ):

    def setStatus( self, msg ):
        self.mainwindow.statusBar().showMessage( msg )        

    def monkeypatch_write( self, str ):
        sys.__stdout__.write( str )
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
        
    def Run( self ):
        self.app = QtGui.QApplication( self.args )

        if ( self.options.path ):
            QtCore.QObject.connect(self.monitor, QtCore.SIGNAL("fileChanged(QString)"), self.processCacheFile)
            self.monitor.Run( self )
            
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
    monitor = False
    fallback = False
    try:
        from PyQt4 import QtCore
        from PyQt4 import QtGui
    except:
        traceback.print_exc()
        print 'There was a problem with the PyQt backend.'
        exit


    if ( os.name == 'nt' ):
        try:
            from evemetrics.file_watcher.win32 import Win32FileMonitor
            monitor = MonitorFactory( Win32FileMonitor )
            monitor.path = options.path
        except ImportError, e:
            traceback.print_exc()
            print "Could not load the non blocking file monitor."
            fallback = True
    elif ( os.name == 'posix' ):
        try:
            from evemetrics.file_watcher.posix import PosixFileMonitor
            monitor = MonitorFactory( PosixFileMonitor )
            monitor.path = options.path
        except ImportError, e:
            traceback.print_exc()
            print "Could not load the non blocking file monitor. Check your pyinotify installation."
            fallback = True
    
    if ( not monitor or fallback ):
        from evemetrics.file_watcher.generic import FileMonitor
        monitor = MonitorFactory( FileMonitor )
        monitor.path = options.path
        for child in monitor.children:
            child.Scan()
    
    if ( options.gui ):
        print 'Starting up GUI subsystem'
        gui = GUI( monitor, processor, options, args )
        gui.Run()
    else:
        print 'Starting up console subsystem'
        console = Console ( monitor, processor, options, args )        
        console.Run()

    if ( not options.gui and options.token is None or options.path is None ):
        raise Exception( 'Insufficient command line data' )

    
