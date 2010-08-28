import logging, platform, os, ConfigParser, string

from evemetrics.file_watcher.factory import MonitorFactory
from evemetrics import parser, uploader
from evemetrics.processor import Processor
from reverence import blue

logger = logging.getLogger('emu')
# this object has process lifespan:
# - it is used to load/save/guess settings
# - it is used to apply/change settings

class Options( object ):
  def __init__(self, default ={}):
    for k,v in default.items():
      self.__setattr__(k, v)
  

class Configuration( object ):

  def __init__( self, gui ):
    self.default = {'poll': 10, 'verbose': False, 'delete' : True, 'token': ''}
    self.options = Options(self.default)
    self.gui = gui
    cp = ConfigParser.ConfigParser()
    cp.read([os.path.expanduser('~/.emu2.ini')])
    if cp.has_section('emu'):
      for k,v in cp.items('emu'):
        if (string.lower(k) == 'verbose' or string.lower(k) == 'delete'): 
          self.options.__setattr__(string.lower(k), True if string.strip(v) == 'True' else False)
        else:
          self.options.__setattr__(string.lower(k), string.strip(v))
    
    logger.info('Current settings:')
    logger.info('  Token: %r' % self.options.token)
    logger.info('  Verbose: %r' % self.options.verbose)
    logger.info('  Delete on upload: %r' % self.options.delete)

  def saveSettings( self ):
    cp = ConfigParser.ConfigParser()
    cp.add_section('emu')
    for k,v in self.default.items():
      cp.set('emu', k, getattr(self.options, k))
    cp.write(open(os.path.expanduser('~/.emu2.ini'), "w"))
    logger.info( 'Configuration saved' )

  # this returns a new monitor, processor, uploader chain based on current settings
  # it will try to guess values if they are missing
  # and will return the monitor if the setup is successful, or None
  # this may be called several times during the lifespan of the process when settings are modified
  def createMonitor( self ):
      if ( self.options.token is None ):
        logger.error( 'Upload token needs to be set.' )
        # no point continuing without a valid token
        return
      
      # the cache path can be explicitely set, if not we rely on autodetection
      checkpath = None #self.options.path
      if ( checkpath is None ):
        logger.info( 'Looking for your EVE cache in the usual locations' )
        if ( platform.system() == 'Windows' ):
          checkpath = os.path.join( os.environ['LOCALAPPDATA'], 'CCP', 'EVE' )
        elif ( platform.system() == 'Linux' ):
          # assuming a standard wine installation, and the same username in wine than local user..
          checkpath = os.path.join( os.path.expanduser( '~/.wine/drive_c/users' ), os.environ['USER'], 'Local Settings/Application Data/CCP/EVE' )
        elif ( platform.system() == 'Darwin' ):
          checkpath = os.path.expanduser( '~/Library/Preferences/EVE Online Preferences/p_drive/Local Settings/Application Data/CCP/EVE' )
      if ( not os.path.isdir( checkpath ) ):
        logger.error( '%r doesn\'t exist. Cache path not found.' % checkpath )
        return

      # now build a list of the cache folders to monitor
      cache_folders = []
      eve_path = None
      cache_path = None
      if ( platform.system() == 'Linux' ):
        # the Windows path tries some path reconstruction, but with only wine 32 bit it's probably easier to just go to the right path
        eve_path = os.path.expanduser( '~/.wine/drive_c/Program Files/CCP/EVE' )
        if ( not os.path.isdir( eve_path ) ):
          logger.error( '%r doesn\'t exist. Base EVE install not found.' % eve_path )
          return
      elif ( platform.system() == 'Darwin' ):
        eve_path = '/Applications/EVE Online.app'
        if ( not os.path.isdir( eve_path ) ):
          logger.error( '%r doesn\'t exist. Base EVE install not found.' % eve_path )
          return

      for installation in os.listdir( checkpath ):
        installation_paths = os.path.join( checkpath, installation, 'cache', 'MachoNet', '87.237.38.200' )
        if ( not os.path.isdir( installation_paths ) ):
          continue
        if not cache_path:
          cache_path = os.path.join( checkpath, installation, 'cache')
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

          logger.debug( 'base_path: %r' % base_path )

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
              #logger.debug( "Set basepath to %s", base_path )
            if ( os.path.isdir( os.path.join( base_path, 'bulkdata' ) ) ):
              # we finally found an installation
              eve_path = base_path
              break
            #print next_folder

      if ( eve_path ):
        logger.info( "Found EVE installation: %s", eve_path )
      else:
        logger.error( "Unable to locate your EVE installation." )
        return

      if ( len( cache_folders ) == 0 ):
          logger.error( 'Could not find any valid cache folders under the cache path %r - invalid cache path?' % checkpath )
          return
      else:
          logger.info( 'Base cache path is %s' % checkpath )
          logger.info( 'Monitoring the following subdirectory(es):' )
          for c in cache_folders:
              logger.info( c.replace( checkpath, '' ) )

      # we can instanciate the filesystem monitor
      monitor = None
      if ( platform.system() == 'Windows' ):
          logger.info( 'Loading win32 file monitor' )
          try:
              from evemetrics.file_watcher.win32 import Win32FileMonitor
              monitor = MonitorFactory( Win32FileMonitor, cache_folders, self )
          except ImportError, e:
              traceback.print_exc()
              logger.error( 'Could not load the win32 optimized file monitor.' )
      elif ( platform.system() == 'Linux' ):
          logger.info( 'Loading inotify file monitor' )
          try:
              from evemetrics.file_watcher.posix import PosixFileMonitor
              monitor = MonitorFactory( PosixFileMonitor, cache_folders, self )                
          except:
              traceback.print_exc()
              logger.error( 'Could not load the Linux optimized file monitor or initialization error. Check your pyinotify installation.' )
          pass

      if ( monitor is None ):
          logger.info( 'Loading generic file monitor' )
          from evemetrics.file_watcher.generic import FileMonitor
          monitor = MonitorFactory( FileMonitor, cache_folders, self )

      # the upload client
      upload_client = uploader.Uploader()
      upload_client.set_token( self.options.token )
      # the processor only needs to know about the upload client
      eve = blue.EVE( eve_path, "Tranquility", -1, "EN", cache_path )
      self.reverence = eve.getconfigmgr()
      processor = Processor( upload_client, self.reverence )
      # points the monitor to the processor, hooks up the signals
      monitor.setProcessor( processor )
      return monitor