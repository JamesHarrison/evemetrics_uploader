from wx.tools.img2py import img2py
import os
try:
  os.remove("evemetrics/icons.py")
except:
  pass
  
img2py('icons/ok.png', 'evemetrics/icons.py', append=True)#,compressed=True, maskClr=None, imgName='ok', icon=False, catalog=True)
img2py('icons/warning.png', 'evemetrics/icons.py', append=True)#,compressed=True, maskClr=None, imgName='warning', icon=False, catalog=True)
img2py('icons/error.png', 'evemetrics/icons.py', append=True)#,compressed=True, maskClr=None, imgName='error', icon=False, catalog=True)
img2py('icons/icon.png', 'evemetrics/icons.py', append=True)#,compressed=True, maskClr=None, imgName='error', icon=False, catalog=True)
img2py('icons/icon_ico.ico', 'evemetrics/icons.py', append=True)#,compressed=True, maskClr=None, imgName='error', icon=False, catalog=True)
