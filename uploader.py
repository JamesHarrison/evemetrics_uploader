#!/usr/bin/env python

import sys, os, time, traceback, pprint, signal, platform, logging, string
import logging.handlers

import threading
from optparse import OptionParser
from cmdline import ParseWithFile, SaveToFile

import wx
from wx import TaskBarIcon
from evemetrics.icons import *

from evemetrics import parser, uploader
from evemetrics.gui_custom import *
from evemetrics.update_checker import UpdateChecker
from evemetrics.configuration import Configuration

from evemetrics.file_watcher.generic import FileMonitor
from evemetrics.file_watcher.factory import MonitorFactory
from evemetrics.gui import EMUMainFrame
from reverence import blue 

#from twisted.internet import wxreactor, reactor
#wxreactor.install()
VERSION = '0.0.4'

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
    self.level = logging.INFO
    self.text_widget = text_widget

  def emit( self, record ):
    try:
      self.text_widget.AppendText(record.getMessage() + "\n")
    except:
      print "Error logging to widget:"
      print record.getMessage()

  def updateLoggingLevel( self, level ):
    self.level = level

class UploaderGui(EMUMainFrame):       
  def __init__(self, parent):
    EMUMainFrame.__init__(self, None)
    self.VERSION = VERSION
    self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    # Set up default logging settings    
    self.logging_handler = LoggingToGUI( self.m_textCtrl_log )
    logging.getLogger('emu').addHandler( self.logging_handler )
    logging.getLogger('emu').setLevel(logging.INFO)
    logger.propagate = False
    logger.info("Starting EVE Metrics Uploader %s" % VERSION)
    # load configuration from file
    self.config = Configuration(self)
  
    # change the logging level if needed
    if ( self.config.options.verbose ):
      self.logging_handler.updateLoggingLevel( logging.DEBUG )
      logging.getLogger('emu').setLevel(logging.DEBUG)
      logging.basicConfig( format = '%(message)s' )
    
    # Initialize the status bar
    self.m_statusBar = MyStatusBar(self)
    self.SetStatusBar(self.m_statusBar)
    
    # Config tab should be selected if the token is empty
    if self.config.options.token != "":
      self.m_notebook.ChangeSelection(0)
      self.setStatus('warning', 'Validating application token.')
    else:
      self.m_notebook.ChangeSelection(1)
      self.setStatus('error', 'No application token set.')
    
    # Update the config tab
    self.m_checkBox_verboseOutput.SetValue(self.config.options.verbose)
    self.m_checkBox_deleteCacheAfterUpload.SetValue(self.config.options.delete)
    self.m_textCtrl_appToken.WriteText(self.config.options.token)
    
    # Start the file monitor
    self.monitor = self.config.createMonitor()
    
    # Fire up the file monitor
    if ( not self.monitor is None ):
      try:
        self.monitor.Run()
      except:
        traceback.print_exc()
        self.monitor = None
      else:
        logger.info( 'Uploader ready' )

    # Events to enable the config apply button        
    self.m_textCtrl_appToken.Bind( wx.EVT_TEXT, self.config_changed )
    self.m_checkBox_deleteCacheAfterUpload.Bind( wx.EVT_CHECKBOX, self.config_changed )
    self.m_checkBox_verboseOutput.Bind( wx.EVT_CHECKBOX, self.config_changed )
    # Event to save save the config
    self.m_button_applyConfig.Bind( wx.EVT_BUTTON, self.apply_configuration )
    
    
    if ( platform.system() == 'Windows' ):
      self.SetIcon(icon_ico.GetIcon())
    else:
      self.SetIcon(icon.GetIcon())
    # set up the tray icon
    self.tbIcon = TaskBarIcon()
    self.tbIcon.SetIcon(icon.GetIcon(), "EVE Metrics Uploader")
    self.tbIcon.Bind(wx.EVT_TASKBAR_LEFT_UP, self.OnTaskBarLeftClick)
    self.tbIcon.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarLeftClick)
    self.Bind(wx.EVT_ICONIZE, self.OnIconify)
    
    # check for new versions
    self.checker = UpdateChecker( self )
    self.checker.Run()
    
  def OnIconify( self, event ):
    if self.IsShown():
      self.Hide()

  def OnTaskBarLeftClick( self, event):
    if self.IsIconized():
      self.Iconize(False)
    if not self.IsShown():
      self.Show(True)
      self.Raise()

  def OnClose(self, event):
    logger.info('Exiting...')
    self.tbIcon.Destroy()
    self.monitor.stop()
    self.Destroy()
    
  def setStatus(self, icon, text):
    self.m_statusBar.setStatus(icon, text)

  def config_changed( self, event ):
    self.m_button_applyConfig.Enable()

  # Virtual event handlers, overide them in your derived class
  def apply_configuration( self, event ):
    # flip back to main tab
    self.m_notebook.SendPageChangingEvent( 0 )
    logger.info('')
    if ( not self.monitor is None ):
        logger.info( 'Tearing down existing monitor' )
        self.monitor.stop()
    logger.info( 'Applying settings' )

    # update verbose status
    self.config.options.verbose = self.m_checkBox_verboseOutput.IsChecked()
    self.config.options.delete = self.m_checkBox_deleteCacheAfterUpload.IsChecked()
    if ( self.config.options.verbose ):
        logging.getLogger('emu').setLevel( logging.DEBUG )
    else:
        logging.getLogger('emu').setLevel( logging.INFO )
    self.config.options.token = self.m_textCtrl_appToken.GetValue()
    try:
        self.monitor = self.config.createMonitor()
        if ( not self.monitor is None ):
            self.monitor.Run()
    except:
        logger.error("Could not restart file monitor: %s" % traceback.print_exc())
        self.monitor = None
    else:
        logger.info( 'Uploader ready' )
        # write settings out to file for next run
        self.config.saveSettings()
    self.m_button_applyConfig.Disable()

if __name__ == "__main__":
  # map stdout into the logging facilities,
  # we will achieve --verbose filtering on print calls that way
  #sys.stdout = wrap_to_lineprint( logging.debug )
  logging.getLogger('emu').setLevel(logging.DEBUG)
  logger = logging.getLogger('emu')

  app = wx.App(0)
  ui = UploaderGui(None)
  ui.Show()
  app.MainLoop()

  


