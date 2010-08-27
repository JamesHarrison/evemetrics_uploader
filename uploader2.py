#!/usr/bin/env python

# First run tutorial.glade through gtk-builder-convert with this command:
# gtk-builder-convert tutorial.glade tutorial.xml
# Then save this file as tutorial.py and make it executable using this command:
# chmod a+x tutorial.py
# And execute it:
# ./tutorial.py
import sys, os, time, traceback, pprint, signal, platform, logging, string

from optparse import OptionParser
from cmdline import ParseWithFile, SaveToFile

from evemetrics import parser, uploader
from evemetrics.configuration import Configuration

from evemetrics.file_watcher.generic import FileMonitor
from evemetrics.file_watcher.factory import MonitorFactory
from reverence import blue 

import pygtk
pygtk.require("2.0")
import gtk
import gobject
gobject.threads_init()

REGION_MAP = {10000001: 'Derelik',10000002: 'The Forge',10000003: 'Vale of the Silent',10000004: 'UUA-F4',10000005: 'Detorid',10000006: 'Wicked Creek',10000007: 'Cache',10000008: 'Scalding Pass',10000009: 'Insmother',10000010: 'Tribute',10000011: 'Great Wildlands',10000012: 'Curse',10000013: 'Malpais',10000014: 'Catch',10000015: 'Venal',10000016: 'Lonetrek',10000017: 'J7HZ-F',10000018: 'The Spire',10000019: 'A821-A',10000020: 'Tash-Murkon',10000021: 'Outer Passage',10000022: 'Stain',10000023: 'Pure Blind',10000025: 'Immensea',10000027: 'Etherium Reach',10000028: 'Molden Heath',10000029: 'Geminate',10000030: 'Heimatar',10000031: 'Impass',10000032: 'Sinq Laison',10000033: 'The Citadel',10000034: 'The Kalevala Expanse',10000035: 'Deklein',10000036: 'Devoid',10000037: 'Everyshore',10000038: 'The Bleak Lands',10000039: 'Esoteria',10000040: 'Oasa',10000041: 'Syndicate',10000042: 'Metropolis',10000043: 'Domain',10000044: 'Solitude',10000045: 'Tenal',10000046: 'Fade',10000047: 'Providence',10000048: 'Placid',10000049: 'Khanid',10000050: 'Querious',10000051: 'Cloud Ring',10000052: 'Kador',10000053: 'Cobalt Edge',10000054: 'Aridia',10000055: 'Branch',10000056: 'Feythabolis',10000057: 'Outer Ring',10000058: 'Fountain',10000059: 'Paragon Soul',10000060: 'Delve',10000061: 'Tenerifis',10000062: 'Omist',10000063: 'Period Basis',10000064: 'Essence',10000065: 'Kor-Azor',10000066: 'Perrigen Falls',10000067: 'Genesis',10000068: 'Verge Vendor',10000069: 'Black Rise'}

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
    txt_buffer = self.text_widget.get_buffer()
    txt_buffer.insert_at_cursor( record.getMessage() + "\n" )
    

  def updateLoggingLevel( self, verbose ):
    self.level = logging.INFO
    if ( verbose ):
      self.level = logging.DEBUG

class UploaderGui(object):       
  def __init__(self, config):
    self.config = config
    self.builder = gtk.Builder()
    self.builder.add_from_file("ui/mainWindow.glade")
    self.builder.connect_signals({ "on_window_destroy" : gtk.main_quit })
    self.window = self.builder.get_object("mainWindow")
    
    self.logging_handler = LoggingToGUI( self.builder.get_object("status") )
    self.logging_handler.updateLoggingLevel( self.logging_handler.level )
    logging.getLogger('').addHandler( self.logging_handler )

    self.monitor = self.config.createMonitor()

    if ( not self.monitor is None ):
      try:
        self.monitor.Run()
      except:
        traceback.print_exc()
        self.monitor = None
      else:
        logging.info( 'Uploader ready' )
    
    self.window.show()

if __name__ == "__main__":
  config = Configuration()

  log_level = logging.INFO
  if ( config.options.verbose ):
      log_level = logging.DEBUG
  logging.basicConfig( level = log_level, format = '%(message)s' )
  # map stdout into the logging facilities,
  # we will achieve --verbose filtering on print calls that way
  #sys.stdout = wrap_to_lineprint( logging.debug )
  sys.stdout = wrap_to_lineprint( logging.debug )
  
  if ( config.options.gui ):
    app = UploaderGui(config)
    gtk.main()
    sys.exit( 0 )

  console = Console( config )
  console.Run()

