#!/usr/bin/env python

import sys, os, time, traceback, pprint, signal, platform, logging, string

from optparse import OptionParser
from cmdline import ParseWithFile, SaveToFile

from evemetrics import parser, uploader

from evemetrics.file_watcher.generic import FileMonitor
from evemetrics.file_watcher.factory import MonitorFactory
from reverence import blue 

REGION_MAP = {10000001: 'Derelik',10000002: 'The Forge',10000003: 'Vale of the Silent',10000004: 'UUA-F4',10000005: 'Detorid',10000006: 'Wicked Creek',10000007: 'Cache',10000008: 'Scalding Pass',10000009: 'Insmother',10000010: 'Tribute',10000011: 'Great Wildlands',10000012: 'Curse',10000013: 'Malpais',10000014: 'Catch',10000015: 'Venal',10000016: 'Lonetrek',10000017: 'J7HZ-F',10000018: 'The Spire',10000019: 'A821-A',10000020: 'Tash-Murkon',10000021: 'Outer Passage',10000022: 'Stain',10000023: 'Pure Blind',10000025: 'Immensea',10000027: 'Etherium Reach',10000028: 'Molden Heath',10000029: 'Geminate',10000030: 'Heimatar',10000031: 'Impass',10000032: 'Sinq Laison',10000033: 'The Citadel',10000034: 'The Kalevala Expanse',10000035: 'Deklein',10000036: 'Devoid',10000037: 'Everyshore',10000038: 'The Bleak Lands',10000039: 'Esoteria',10000040: 'Oasa',10000041: 'Syndicate',10000042: 'Metropolis',10000043: 'Domain',10000044: 'Solitude',10000045: 'Tenal',10000046: 'Fade',10000047: 'Providence',10000048: 'Placid',10000049: 'Khanid',10000050: 'Querious',10000051: 'Cloud Ring',10000052: 'Kador',10000053: 'Cobalt Edge',10000054: 'Aridia',10000055: 'Branch',10000056: 'Feythabolis',10000057: 'Outer Ring',10000058: 'Fountain',10000059: 'Paragon Soul',10000060: 'Delve',10000061: 'Tenerifis',10000062: 'Omist',10000063: 'Period Basis',10000064: 'Essence',10000065: 'Kor-Azor',10000066: 'Perrigen Falls',10000067: 'Genesis',10000068: 'Verge Vendor',10000069: 'Black Rise'}
class Processor( object ):
    def __init__( self, upload_client, eve_path ):
        self.upload_client = upload_client
        self.eve_path = eve_path
        eve = blue.EVE( eve_path )
        self.reverence = eve.getconfigmgr()


    def OnNewFile( self, pathname ):
        try:
            if ( pathname.__class__ == QtCore.QString ):
                pathname = str( pathname )
            print 'OnNewFile: %s' % pathname
            if ( os.path.splitext( pathname )[1] != '.cache' ):
                logging.debug( 'Not a .cache, skipping' )
                return
            try:
                parsed_data = parser.parse( pathname )
            except IOError:
                # I was retrying initially, but some files are deleted before we get a chance to parse them,
                # which is what's really causing this
                logging.warning( 'IOError exception, skipping' )
                return
            if ( parsed_data is None ):
                logging.debug( 'No data parsed' )
                return
            t = self.reverence.invtypes.Get(parsed_data[2])
            
            logging.debug( 'Call %s, regionID %d, typeID %d' % ( parsed_data[0], parsed_data[1], parsed_data[2] ) )

            ret = self.upload_client.send(parsed_data)
            if ( ret ):
                if ( parsed_data[0] == 'GetOldPriceHistory' ):
                    logging.info( 'Uploaded price history for %s in %s' % (t.name, REGION_MAP.get(parsed_data[1], 'Unknown') ) )
                else:
                    logging.info( 'Uploaded orders for %s in %s' % (t.name, REGION_MAP.get(parsed_data[1], 'Unknown') ) )
                logging.debug( 'Removing cache file %s' % pathname )
                os.remove( pathname )
            else:
                logging.error( 'Could not upload file')
                # We should manage some sort of backlog if evemetrics is down
        except:
            traceback.print_exc()
        else:
            print ret

# present a stream friendly API (for instance to replace sys.stdout)
# and pass this to a callable that's line based
class wrap_to_lineprint( object ):
    def __init__( self, c ):
        self.c = c # a callable
        self.line = ''

    def write( self, s ):
        self.line += s
        spl = self.line.split('\n')
        if ( len( spl ) >= 2 ):
            while ( len( spl ) > 1 ):
                self.c( spl[0] )
                spl = spl[1:]
            assert( len( spl ) == 1 )
            self.line = spl[0]

class Console( object ):
    def __init__( self, config ):
        self.config = config

    def Run( self ):
        self.monitor = self.config.createMonitor()

        if ( self.monitor is None ):
            logging.error( 'Incorrect or insufficient command line options for headless operation.' )
            return

        self.app = QtCore.QCoreApplication( [] )

        # so Ctrl-C works
        signal.signal( signal.SIGINT, signal.SIG_DFL )

        self.monitor.Run()

        self.app.exec_()

class LoggingToGUI( logging.Handler ):
    def __init__( self, text_widget ):
        logging.Handler.__init__( self )
        self.text_widget = text_widget

    def emit( self, record ):
        self.text_widget.appendPlainText( record.getMessage() )

    def updateLoggingLevel( self, verbose ):
        self.level = logging.INFO
        if ( verbose ):
            self.level = logging.DEBUG

class GUI( object ):
    def __init__( self, config ):
        self.config = config
        self.stdout_line = ""

    def setStatus( self, msg ):
        self.mainwindow.statusBar().showMessage( msg )        

    def browsePath( self ):
        fileName = QtGui.QFileDialog.getExistingDirectory( self.mainwindow, 'Select your EvE directory (where eve.exe resides)' )

    def applyPrefs( self ):
        # flip back to main tab
        self.tabs.setCurrentIndex( 0 )
        if ( not self.monitor is None ):
            logging.info( 'Tearing down existing monitor' )
            self.monitor = None
        logging.info( 'Applying settings' )

        # update verbose status
        self.config.options.verbose = self.verbose_box.isChecked()
        if ( self.config.options.verbose ):
            logging.getLogger('').setLevel( logging.DEBUG )
        else:
            logging.getLogger('').setLevel( logging.INFO )
        self.logging_handler.updateLoggingLevel( self.config.options.verbose )

        self.config.options.token = str( self.token_edit.text() )
        try:
            self.monitor = self.config.createMonitor()
            if ( not self.monitor is None ):
                self.monitor.Run()
        except:
            traceback.print_exc()
            self.monitor = None
        else:
            logging.info( 'Uploader ready' )
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
        # I can't figure the pyqt way, so passing the numeric value
#        self.status.setLineWrapMode( QtGui.QTextEdit.NoWrap )
        self.status.setLineWrapMode( 0 )
        self.status.setMaximumBlockCount( self.config.options.lines )
#        sys.stdout = stdout_wrap( self.monkeypatch_write )

        self.logging_handler = LoggingToGUI( self.status )
        self.logging_handler.updateLoggingLevel( self.logging_handler.level )
        logging.getLogger('').addHandler( self.logging_handler )

#        logging.info('test info line')
#        logging.debug('test debug line')
#        print 'test print line'

        # tabs
        self.tabs = QtGui.QTabWidget()
        self.tabs.addTab( self.status, 'Activity' )

        prefs_layout = QtGui.QFormLayout()
        self.token_edit = QtGui.QLineEdit()
        prefs_layout.addRow( QtGui.QLabel( 'User Token:' ), self.token_edit )
        self.verbose_box = QtGui.QCheckBox()
        prefs_layout.addRow( QtGui.QLabel( 'Verbose:' ), self.verbose_box )
        
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
            # couldn't get the python right for http://doc.qt.nokia.com/4.6/qt.html#CheckState-enum
            if ( self.config.options.verbose ):
                self.verbose_box.setCheckState( 2 )
            else:
                self.verbose_box.setCheckState( 0 )

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
                logging.info( 'Uploader ready' )
        
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
        self.defaults = { 'poll' : 10, 'gui' : True, 'lines' : 1000, 'verbose' : False }
        self.do_not_save = [ 'verbose' ]
        self.parser = OptionParser()
        # core
        self.parser.add_option( '-t', '--token', dest = 'token', help = 'EVE Metrics uploader token - see http://www.eve-metrics.com/downloads' )
        self.parser.add_option( '-p', '--path', dest = 'path', help = 'EVE cache path (top level directory)' )
        self.parser.add_option( '-v', '--verbose', action = 'store_true', dest = 'verbose', help = 'Be verbose (default %r)' % self.defaults['verbose'] )
        # UI
        self.parser.add_option( '-n', '--nogui', action = 'store_false', dest = 'gui', help = 'Run in text mode' )
        self.parser.add_option( '-g', '--gui', action = 'store_true', dest = 'gui', help = 'Run in GUI mode (default)' )
        # filesystem alteration monitoring
        self.parser.add_option( '-P', '--poll', dest = 'poll', help = 'Generic file monitor: poll every n seconds (default %d)' % self.defaults['poll'] )
        self.parser.add_option( '-l', '--lines', dest = 'lines', help = 'How many scrollback lines in the GUI (default %d)' % self.defaults['lines'] )

        ( self.options, self.args ) = ParseWithFile( self.parser, self.defaults, filename = 'eve_uploader.ini', do_not_save = self.do_not_save )

        print 'Current settings:'
        print '  Token: %r' % self.options.token
        print '  Path: %r' % self.options.path
        print '  GUI: %r' % self.options.gui

    def saveSettings( self ):
        SaveToFile( self.options, self.parser, self.defaults, filename = 'eve_uploader.ini', do_not_save = self.do_not_save )
        logging.info( 'Configuration saved' )

    # this returns a new monitor, processor, uploader chain based on current settings
    # it will try to guess values if they are missing
    # and will return the monitor if the setup is successful, or None
    # this may be called several times during the lifespan of the process when settings are modified
    def createMonitor( self ):
        if ( self.options.token is None ):
            logging.error( 'Upload token needs to be set.' )
            # no point continuing without a valid token
            return
        
        # the cache path can be explicitely set, if not we rely on autodetection
        checkpath = self.options.path
        if ( checkpath is None ):
            logging.info( 'Looking for your EVE cache in the usual locations' )
            if ( platform.system() == 'Windows' ):
                checkpath = os.path.join( os.environ['LOCALAPPDATA'], 'CCP', 'EVE' )
            elif ( platform.system() == 'Linux' ):
                # assuming a standard wine installation, and the same username in wine than local user..
                checkpath = os.path.join( os.path.expanduser( '~/.wine/drive_c/users' ), os.environ['USER'], 'Local Settings/Application Data/CCP/EVE' )
            elif ( platform.system() == 'Darwin' ):
                checkpath = os.path.expanduser( '~/Library/Preferences/EVE Online Preferences/p_drive/Local Settings/Application Data/CCP/EVE' )
        if ( not os.path.isdir( checkpath ) ):
            logging.error( '%r doesn\'t exist. Cache path not found.' % checkpath )
            return

        # now build a list of the cache folders to monitor
        cache_folders = []
        eve_path = None
        if ( platform.system() == 'Linux' ):
            # the Windows path tries some path reconstruction, but with only wine 32 bit it's probably easier to just go to the right path
            eve_path = os.path.expanduser( '~/.wine/drive_c/Program Files/CCP/EVE' )
            if ( not os.path.isdir( eve_path ) ):
                logging.error( '%r doesn\'t exist. Base EVE install not found.' % eve_path )
                return
        elif ( platform.system() == 'Darwin' ):
            eve_path = '/Applications/EVE Online.app/Contents/Resources/transgaming/c_drive/Program Files/CCP/EVE'
            if ( not os.path.isdir( eve_path ) ):
                logging.error( '%r doesn\'t exist. Base EVE install not found.' % eve_path )
                return

        for installation in os.listdir( checkpath ):
            installation_paths = os.path.join( checkpath, installation, 'cache', 'MachoNet', '87.237.38.200' )
            if ( not os.path.isdir( installation_paths ) ):
                continue
            # lets find the newest machonet version
            versions = [ int(x) for x in os.listdir( installation_paths ) ]
            versions.sort()
            testdir = os.path.join( installation_paths, str( versions.pop() ), 'CachedMethodCalls' )
            if ( not os.path.isdir( testdir ) ):
                continue
            cache_folders.append( testdir )

            # Windows only .. doesn't work as-is on Linux (case sensitivity etc.) and probably not that necessary
            if ( not eve_path ):
              # we need to get a eve installation path to display information about the item/region uploaded
              parts = installation.split( '_' )
              parts.pop( len( parts ) - 1 )
#              print 'installation: %r parts: %r' % ( installation, parts )
              if ( platform.system() == 'Windows' ):
                base_path = "%s:\\" % parts.pop( 0 )

              print 'base_path: %r' % base_path

              next_folder = None
              while ( not eve_path ):
                if ( len(parts) == 0 ):
                  break
                if ( next_folder ):
                  next_folder = "%s %s" % ( next_folder, parts.pop( 0 ) )
                  if ( len(parts) != 0 and parts[0] == '(x86)' ):
                    next_folder = "%s %s" % ( next_folder, parts.pop( 0 ) )  
                else:
                  next_folder = parts.pop( 0 )
                if ( os.path.isdir( os.path.join( base_path, next_folder ) ) ):
                  base_path = os.path.join( base_path, next_folder )
                  next_folder = ""
                  #logging.debug( "Set basepath to %s", base_path )
                if ( os.path.isdir( os.path.join( base_path, 'bulkdata' ) ) ):
                  # we finally found an installation
                  eve_path = base_path
                  break
                #print next_folder

        if ( eve_path ):
          logging.info( "Found EVE installation: %s", eve_path )
        else:
          logging.error( "Unable to locate your EVE installation." )
          return

        if ( len( cache_folders ) == 0 ):
            logging.error( 'Could not find any valid cache folders under the cache path %r - invalid cache path?' % checkpath )
            return
        else:
            logging.info( 'Base cache path is %s' % checkpath )
            logging.info( 'Monitoring the following subdirectory(es):' )
            for c in cache_folders:
                logging.info( c.replace( checkpath, '' ) )

        # we can instanciate the filesystem monitor
        monitor = None
        if ( platform.system() == 'Windows' ):
            logging.info( 'Loading win32 file monitor' )
            try:
                from evemetrics.file_watcher.win32 import Win32FileMonitor
                monitor = MonitorFactory( Win32FileMonitor, cache_folders, self.options )
            except ImportError, e:
                traceback.print_exc()
                logging.error( 'Could not load the win32 optimized file monitor.' )
        elif ( platform.system() == 'Linux' ):
            logging.info( 'Loading inotify file monitor' )
            try:
                from evemetrics.file_watcher.posix import PosixFileMonitor
                monitor = MonitorFactory( PosixFileMonitor, cache_folders, self.options )                
            except:
                traceback.print_exc()
                logging.error( 'Could not load the Linux optimized file monitor or initialization error. Check your pyinotify installation.' )
            pass

        if ( monitor is None ):
            logging.info( 'Loading generic file monitor' )
            from evemetrics.file_watcher.generic import FileMonitor
            monitor = MonitorFactory( FileMonitor, cache_folders, self.options )

        # the upload client
        upload_client = uploader.Uploader()
        upload_client.set_token( self.options.token )

        # the processor only needs to know about the upload client
        processor = Processor( upload_client, eve_path )

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
        logging.error( 'There was a problem with the PyQt backend.' )
        sys.exit( -1 )

    config = Configuration()

    log_level = logging.INFO
    if ( config.options.verbose ):
        log_level = logging.DEBUG
    logging.basicConfig( level = log_level, format = '%(message)s' )
    # map stdout into the logging facilities,
    # we will achieve --verbose filtering on print calls that way
    sys.stdout = wrap_to_lineprint( logging.debug )

    if ( config.options.gui ):
        gui = GUI( config )
        gui.Run()
        sys.exit( 0 )

    console = Console( config )
    console.Run()
