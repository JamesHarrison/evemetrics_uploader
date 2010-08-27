from optparse import OptionParser
from cmdline import ParseWithFile, SaveToFile
import logging, platform, os

from evemetrics.file_watcher.factory import MonitorFactory
from evemetrics import parser, uploader
from evemetrics.processor import Processor
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
            eve_path = '/Applications/EVE Online.app'
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