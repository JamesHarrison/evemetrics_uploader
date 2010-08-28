import wx
import time
from evemetrics.icons import *
class MyStatusBar(wx.StatusBar):
  def __init__(self, parent):
    wx.StatusBar.__init__(self, parent)
    self.SetFieldsCount(2)
    self.SetStatusWidths([20,-1])

    self.status_oke = wx.StaticBitmap(self, -1, ok.GetBitmap())
    self.status_warning = wx.StaticBitmap(self, -1, warning.GetBitmap())
    self.status_error = wx.StaticBitmap(self, -1, error.GetBitmap())
    self.status_oke.Hide()
    self.status_warning.Hide()
    self.status_error.Hide()
    
    self.icon = self.status_oke
    self.SetStatusText('', 1)
    self.Bind(wx.EVT_SIZE, self.OnSize)
    
  def setStatus(self, icon, text):
    self.SetStatusText(text, 1)
    if (icon == 'ok'):
      if self.icon == self.status_oke:
        return 
      self.icon.Hide()
      self.icon = self.status_oke
      self.icon.Show()
    elif(icon == 'warning'):
      if self.icon == self.status_warning:
        return
      self.icon.Hide()
      self.icon = self.status_warning
      self.icon.Show()
    elif(icon == 'error'):
      if self.icon == self.status_error:
        return
      self.icon.Hide()
      self.icon = self.status_error
      self.icon.Show()
    self.PlaceIcon()
    
  def PlaceIcon(self):
    if self.icon:
      rect = self.GetFieldRect(0)
      self.icon.SetPosition((rect.x+2, rect.y+2))

  def OnSize(self, event):
    self.PlaceIcon()
