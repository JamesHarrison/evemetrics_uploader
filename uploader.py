#!/usr/bin/env python

import sys, os, time, traceback, pprint, signal, platform

from optparse import OptionParser
from cmdline import ParseWithFile, SaveToFile

from evemetrics import parser, uploader

from evemetrics.file_watcher.generic import FileMonitor
from evemetrics.file_watcher.factory import MonitorFactory

class Processor( object ):
    def __init__( self, upload_client ):
        self.upload_client = upload_client

    def OnNewFile( self, pathname ):
        print 'OnNewFile: %r' % pathname
        try:
            if ( pathname.__class__ == QtCore.QString ):
                pathname = str( pathname )
            print 'New or modified file: %s' % pathname
            if ( os.path.splitext( pathname )[1] != '.cache' ):
                print 'Not a .cache, skipping'
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
        
class Console( object ):
    def __init__( self, config ):
        self.config = config

    def Run( self ):
        self.monitor = self.config.createMonitor()

        if ( self.monitor is None ):
            print 'Incorrect or insufficient command line options for headless operation.'
            return

        self.app = QtCore.QCoreApplication( [] )

        # so Ctrl-C works
        signal.signal( signal.SIGINT, signal.SIG_DFL )

        self.monitor.Run()

        self.app.exec_()

class GUI( object ):
    def __init__( self, config ):
        self.config = config
        self.stdout_line = ""

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

    def applyPrefs( self ):
        # flip back to main tab
        self.tabs.setCurrentIndex( 0 )
        if ( not self.monitor is None ):
            print 'Tearing down existing monitor'
            self.monitor = None
        print 'Applying settings'
        self.config.options.token = str( self.token_edit.text() )
        try:
            self.monitor = self.config.createMonitor()
            if ( not self.monitor is None ):
                self.monitor.Run()
        except:
            traceback.print_exc()
            self.monitor = None
        else:
            print 'Cache monitoring enabled.'
            # write settings out to file for next run
            self.config.saveSettings()
        
    def Run( self ):
        self.app = QtGui.QApplication( [] )

        # create all the GUI elements first

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
# disable the cache browse for now - auto detection should suffice
#        self.path_browse = QtGui.QPushButton( 'Change' )
#        self.app.connect( self.path_browse, QtCore.SIGNAL( 'clicked()' ), self.browsePath )
#        prefs_layout.addRow( QtGui.QLabel( 'EvE cache path:' ), self.path_browse )
        prefs_widg = QtGui.QWidget()
        prefs_widg.setLayout( prefs_layout )

        top_prefs_layout = QtGui.QVBoxLayout()
        top_prefs_layout.addWidget( QtGui.QLabel( 'Your upload token is available from\nhttp://www.eve-metrics.com/downloads' ) )
        top_prefs_layout.addWidget( prefs_widg )
        self.apply_prefs_button = QtGui.QPushButton( 'Apply' )
        top_prefs_layout.addWidget( self.apply_prefs_button )
        self.app.connect( self.apply_prefs_button, QtCore.SIGNAL( 'clicked()' ), self.applyPrefs )

        top_prefs_widg = QtGui.QWidget()
        top_prefs_widg.setLayout( top_prefs_layout )
        
        self.tabs.addTab( top_prefs_widg, 'Preferences' )

        if ( not self.config.options.token is None ):
            self.token_edit.setText( self.config.options.token )

        self.mainwindow.setCentralWidget( self.tabs )
        self.mainwindow.show()
        self.mainwindow.raise_()

        self.monitor = self.config.createMonitor()

        if ( not self.monitor is None ):
            try:
                self.monitor.Run()
            except:
                traceback.print_exc()
                self.monitor = None
            else:
                print 'Cache monitoring enabled.'
        
        if ( self.monitor is None ):
            # bring the prefs tab to front to set the config
            self.tabs.setCurrentIndex( 1 )

        sys.exit( self.app.exec_() )

# this object has process lifespan:
# - it is used to load/save/guess settings
# - it is used to apply/change settings
class Configuration( object ):

    def __init__( self ):
        # using cmdline helper module for disk backing
        # pydoc ./cmdline.py
        # defaults are handled separately with the cmdline module
        self.defaults = { 'poll' : 10, 'gui' : True }
        self.parser = OptionParser()
        # core
        self.parser.add_option( '-t', '--token', dest = 'token', help = 'EVE Metrics uploader token - see http://www.eve-metrics.com/downloads' )
        self.parser.add_option( '-p', '--path', dest = 'path', help = 'EVE cache path (top level directory)' )
        # UI
        self.parser.add_option( '-n', '--nogui', action = 'store_false', dest = 'gui', help = 'Run in text mode' )
        self.parser.add_option( '-g', '--gui', action = 'store_true', dest = 'gui', help = 'Run in GUI mode (default)' )
        # filesystem alteration monitoring
        self.parser.add_option( '-P', '--poll', dest = 'poll', help = 'Poll every n seconds (default %d)' % self.defaults['poll'] )

        ( self.options, self.args ) = ParseWithFile( self.parser, self.defaults, filename = 'eve_uploader.ini' )

        print 'Current settings:'
        print '  Token: %r' % self.options.token
        print '  Path: %r' % self.options.path
        print '  GUI: %r' % self.options.gui

    def saveSettings( self ):
        SaveToFile( self.options, self.parser, self.defaults, filename = 'eve_uploader.ini' )
        print 'Configuration saved'

    # this returns a new monitor, processor, uploader chain based on current settings
    # it will try to guess values if they are missing
    # and will return the monitor if the setup is successful, or None
    # this may be called several times during the lifespan of the process when settings are modified
    def createMonitor( self ):
        if ( self.options.token is None ):
            print 'Upload token needs to be set.'
            # no point continuing without a valid token
            return
        
        # the cache path can be explicitely set, if not we rely on autodetection
        checkpath = self.options.path
        if ( checkpath is None ):
            print 'Looking for your EVE cache in the usual locations'
            if ( platform.system() == 'Windows' ):
                checkpath = os.path.join( os.environ['LOCALAPPDATA'], 'CCP', 'EVE' )
            elif ( platform.system() == 'Linux' ):
                # assuming a standard wine installation, and the same username in wine than local user..
                checkpath = os.path.join( os.path.expanduser( '~/.wine/drive_c/users' ), os.environ['USER'], 'Local Settings/Application Data/CCP/EVE' )
            elif ( platform.system() == 'Darwin' ):
                checkpath = os.path.expanduser( '~/Library/Preferences/EVE Online Preferences/p_drive/Local Settings/Application Data/CCP/EVE' )
        if ( not os.path.isdir( checkpath ) ):
            print '%r doesn\'t exist. Cache path not found.' % checkpath
            return

        print 'Base cache path is %r' % checkpath
        
        # now build a list of the cache folders to monitor
        cache_folders = []
        for installation in os.listdir( checkpath ):
            testdir = os.path.join( checkpath, installation, 'cache', 'MachoNet', '87.237.38.200', '235', 'CachedMethodCalls' )
            if ( not os.path.isdir( testdir ) ):
                continue
            cache_folders.append( testdir )

        if ( len( cache_folders ) == 0 ):
            print 'Could not find any valid cache folders under the cache path %r - invalid cache path?' % checkpath
            return

        print 'Monitoring the following directory(es):'
        for c in cache_folders:
            print c

        # we can instanciate the filesystem monitor
        monitor = None
        if ( False and platform.system() == 'Windows' ):
            print "Loading the Win32FileMonitor"
            try:
                from evemetrics.file_watcher.win32 import Win32FileMonitor
                monitor = MonitorFactory( Win32FileMonitor, cache_folders )
            except ImportError, e:
                traceback.print_exc()
                print "Could not load the win32 optimized file monitor."
        elif ( platform.system() == 'Linux' ):
            print "Loading the PosixFileMonitor"
            try:
                from evemetrics.file_watcher.posix import PosixFileMonitor
                monitor = MonitorFactory( PosixFileMonitor, cache_folders )
            except ImportError, e:
                traceback.print_exc()
                print "Could not load the non blocking file monitor. Check your pyinotify installation."
            pass

        if ( monitor is None ):
            print "Loading the GenericFileMonitor"
            from evemetrics.file_watcher.generic import FileMonitor
            monitor = MonitorFactory( FileMonitor, cache_folders )

        # the upload client
        upload_client = uploader.Uploader()
        upload_client.set_token( self.options.token )

        # the processor only needs to know about the upload client
        processor = Processor( upload_client )

        # points the monitor to the processor, hooks up the signals
        monitor.setProcessor( processor )

        return monitor

if ( __name__ == '__main__' ):
    # start by verifying PyQt presence
    try:
        from PyQt4 import QtCore
        from PyQt4 import QtGui
    except:
        traceback.print_exc()
        print 'There was a problem with the PyQt backend.'
        sys.exit( -1 )

    config = Configuration()

    if ( config.options.gui ):
        gui = GUI( config )
        gui.Run()
        sys.exit( 0 )

    console = Console( config )
    console.Run()
