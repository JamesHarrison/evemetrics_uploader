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
    conn = httplib.HTTPConnection("github.com")
    conn.request("GET", "/JamesHarrison/evemetrics_uploader/raw/master/VERSION")
    resp = conn.getresponse()
    if resp.status != 200:
      return
    data = resp.read()
    #data = "0.0.2\nNew neat version online grab it, while it's hot!\nhttp://github.com/downloads/JamesHarrison/evemetrics_uploader/EVEMetricsUploaderSetup.exe"
    (version, notice, url) = data.split('\n',3)
    
    (c_may, c_min, c_p) = (int(i) for i in self.gui.VERSION.split('.'))
    (n_may, n_min, n_p) = (int(i) for i in version.split('.'))
    if ((n_may >= c_may and n_min >= c_min and n_p > c_p) or
        (n_may >= c_may and n_min > c_min) or
        (n_may > c_may)  
       ):
      dial = wx.MessageDialog(None, 'Are you sure to quit?', 'Question', 
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

      update = wx.MessageDialog(None,"A new uploader version has been released:\n%s" % notice, "Download update?", wx.YES_NO | wx.ICON_QUESTION)
      if not self.gui.IsShown():
        self.gui.Show(True)
        self.gui.Raise()
      if update.ShowModal() == wx.ID_YES:
        webbrowser.open(url)
