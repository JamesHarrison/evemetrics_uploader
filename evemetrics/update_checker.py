from threading import Thread
import httplib, urllib, hashlib, logging
import wx

import webbrowser

logger = logging.getLogger('emu')
from uploader import *
class UpdateChecker ( Thread):
  def __init__( self, gui ):
    Thread.__init__(self)
    self.gui = gui

  def Run( self ):
    self.start()
    
  def run( self ):
    conn = httplib.HTTPSConnection("github.com")
    conn.request("GET", "/JamesHarrison/evemetrics_uploader/raw/master/VERSION")
    resp = conn.getresponse()

    if resp.status != 200:
      return
    data = resp.read()

    (version, notice, url) = data.split('\n',3)
    logger.debug("Current version: %s" % self.gui.VERSION)
    logger.debug("New      version: %s" % version)
    (c_may, c_min, c_p) = (int(i) for i in self.gui.VERSION.split('.'))
    (n_may, n_min, n_p) = (int(i) for i in version.split('.'))
    if ((n_may >= c_may and n_min >= c_min and n_p > c_p) or
        (n_may >= c_may and n_min > c_min) or
        (n_may > c_may)  
       ):

      update = wx.MessageDialog(None,"A new uploader version has been released:\n%s" % notice, "Download update?", wx.YES_NO | wx.ICON_QUESTION)
      if not self.gui.IsShown():
        self.gui.Show(True)
        self.gui.Raise()
      if update.ShowModal() == wx.ID_YES:
        webbrowser.open(url)
