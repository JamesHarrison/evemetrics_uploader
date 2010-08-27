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
from evemetrics.gui import EMUMainFrame
from reverence import blue 

from wx import *
#from twisted.internet import wxreactor, reactor
#wxreactor.install()


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

class LoggingToGUI( logging.Handler ):
  def __init__( self, text_widget ):
    logging.Handler.__init__( self )
    self.text_widget = text_widget

  def emit( self, record ):
    self.text_widget.AppendText(record.getMessage() + "\n")
    

  def updateLoggingLevel( self, verbose ):
    self.level = logging.INFO
    if ( verbose ):
      self.level = logging.DEBUG

class UploaderGui(EMUMainFrame):       
  def __init__(self, parent, config):
    EMUMainFrame.__init__(self, None, config)
    self.config = config
    self.m_checkBox_verboseOutput.SetValue(config.options.verbose)
    self.m_textCtrl_appToken.WriteText(config.options.token)
      
    
    self.logging_handler = LoggingToGUI( self.m_textCtrl_log )
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
        
      
  # Virtual event handlers, overide them in your derived class
  def apply_configuration( self, event ):
    # flip back to main tab
    self.m_notebook.SendPageChangingEvent( 0 )
    logging.info('')
    if ( not self.monitor is None ):
        logging.info( 'Tearing down existing monitor' )
        self.monitor = None
    logging.info( 'Applying settings' )

    # update verbose status
    self.config.options.verbose = self.m_checkBox_verboseOutput.IsChecked()
    self.config.options.delete = self.m_checkBox_deleteCacheAfterUpload.IsChecked()
    if ( self.config.options.verbose ):
        logging.getLogger('').setLevel( logging.DEBUG )
    else:
        logging.getLogger('').setLevel( logging.INFO )
    print self.m_textCtrl_appToken.GetValue()
    self.config.options.token = self.m_textCtrl_appToken.GetValue()
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
        print self.config.options.token
        self.config.saveSettings()

  


if __name__ == "__main__":
  config = Configuration()

  log_level = logging.INFO
  if ( config.options.verbose ):
      log_level = logging.DEBUG
  logging.basicConfig( level = log_level, format = '%(message)s' )
  # map stdout into the logging facilities,
  # we will achieve --verbose filtering on print calls that way
  #sys.stdout = wrap_to_lineprint( logging.debug )
  app = wx.App(0)
  ui = UploaderGui(None, config)
  ui.Show()
  app.MainLoop()

  


