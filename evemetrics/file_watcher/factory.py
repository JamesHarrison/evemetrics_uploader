import sys, os, time, traceback, platform

from .generic import FileMonitor
from threading import Thread
from Queue import PriorityQueue
import logging
logger = logging.getLogger('emu')

class MonitorFactory( Thread ):
    
  def __init__( self, monitorClass, valid_paths, config ):
    Thread.__init__( self )
    self.processor = None
    self.config = config
    self.valid_paths = valid_paths
    self.monitorClass = monitorClass
    self.children = []
    self.upload_queue = PriorityQueue()
    
    for path in self.valid_paths:
      # the children emit signals to this factor to communicate back changes
      self.children.append( self.monitorClass( self, path, config ) )

  def queue(self,item):
    if not self.config.tokenValid:
      return
    logger.debug("(%s) Queueing file %s" % (self.upload_queue.qsize(), item))
    self.upload_queue.put(item)
  
  def stop( self ):
    for monitor in self.children:
      monitor.__del__()
      monitor.join()
    self.upload_queue.put((0,None))
    # Not waiting for the thread isn't nice but that way we get out fast!
    # FIXME
    #self.join()
      
  def Run( self ):
    for child in self.children:
      child.Run()
    self.start()

  def run( self ):
    # On startup check the token for vadility
    (valid, user) = self.testToken()
    if valid:
      self.config.tokenValid = True
      self.config.gui.setStatus('ok', "Authenticated as %s. Ready to upload data." % user)
    elif user == 'error':
      self.config.gui.setStatus('error', 'Invalid response from server.')
    else:
      self.config.tokenValid = False
      self.config.gui.setStatus('error', 'Invalid application token.')
    
    # Work on the upload queue
    while True:
      (prio, item) = self.upload_queue.get()
      if item is None:
        break

      if not self.processor.OnNewFile(item):
        logger.warn("Error uploading file, requeueing")
        self.queue(item)
        time.sleep(1)
      self.upload_queue.task_done()
    # Done.  Indicate that sentinel was received and return
    self.upload_queue.task_done()
    
    return

  def setProcessor( self, processor ):
    self.processor = processor
      
  def testToken( self ):
    return self.processor.upload_client.check_token()