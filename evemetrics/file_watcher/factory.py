import sys, os, time, traceback, platform

from .generic import FileMonitor
from threading import Thread
import logging
class MonitorFactory( Thread ):
    
    def __init__( self, monitorClass, valid_paths, config ):
        Thread.__init__( self )
        self.processor = None
        self.config = config
        self.valid_paths = valid_paths
        self.monitorClass = monitorClass
        self.children = []

        for path in self.valid_paths:
            # the children emit signals to this factor to communicate back changes
            self.children.append( self.monitorClass( self, path, config ) )
    def stop( self ):
      for monitor in self.children:
        monitor.__del__()
        monitor.join()
        
    def Run( self ):
        for child in self.children:
            child.Run()
        self.start()

    def run( self ):
        (valid, user) = self.testToken()
        if valid:
          self.config.gui.setStatus('ok', "Authenticated as %s. Ready to upload data." % user)
        elif user == 'error':
          self.config.gui.setStatus('error', 'Invalid response from server.')
        else:
          self.config.gui.setStatus('error', 'Invalid application token.')


    def setProcessor( self, processor ):
        self.processor = processor
        
    def testToken( self ):
      return self.processor.upload_client.check_token()