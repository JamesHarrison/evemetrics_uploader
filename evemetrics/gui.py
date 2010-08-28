# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version May  4 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx, logging

###########################################################################
## Class EMUMainFrame
###########################################################################

class EMUMainFrame ( wx.Frame ):
  
  def __init__( self, parent ):
    wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"EVE Metrics Uploader 2", pos = wx.DefaultPosition, size = wx.Size( 380,500 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )
    
    self.SetSizeHintsSz( wx.Size( 380,500 ), wx.DefaultSize )
    
    bSizer1 = wx.BoxSizer( wx.VERTICAL )
    
    self.m_notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_statusPanel = wx.Panel( self.m_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
    gSizer1 = wx.GridSizer( 1, 1, 0, 0 )
    
    self.m_textCtrl_log = wx.TextCtrl( self.m_statusPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL )
    gSizer1.Add( self.m_textCtrl_log, 0, wx.ALL|wx.EXPAND, 5 )
    
    self.m_statusPanel.SetSizer( gSizer1 )
    self.m_statusPanel.Layout()
    gSizer1.Fit( self.m_statusPanel )
    self.m_notebook.AddPage( self.m_statusPanel, u"Status", True )
    self.m_configurePanel = wx.Panel( self.m_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
    bSizer_Config = wx.BoxSizer( wx.VERTICAL )
    
    sbSizer_Basic = wx.StaticBoxSizer( wx.StaticBox( self.m_configurePanel, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )
    
    fgSizer1 = wx.FlexGridSizer( 3, 2, 0, 0 )
    fgSizer1.SetFlexibleDirection( wx.BOTH )
    fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
    
    self.m_staticText9 = wx.StaticText( self.m_configurePanel, wx.ID_ANY, u"Application Token", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_staticText9.Wrap( -1 )
    fgSizer1.Add( self.m_staticText9, 0, wx.ALL, 5 )
    
    self.m_textCtrl_appToken = wx.TextCtrl( self.m_configurePanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,-1 ), 0 )
    fgSizer1.Add( self.m_textCtrl_appToken, 0, wx.ALL, 5 )
    
    
    fgSizer1.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
    
    self.m_hyperlink1 = wx.HyperlinkCtrl( self.m_configurePanel, wx.ID_ANY, u"Don't know your token?", u"http://www.eve-metrics.com/downloads/", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
    fgSizer1.Add( self.m_hyperlink1, 0, wx.ALL, 5 )
    
    self.m_staticText8 = wx.StaticText( self.m_configurePanel, wx.ID_ANY, u"Delete cache file after upload", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_staticText8.Wrap( -1 )
    fgSizer1.Add( self.m_staticText8, 0, wx.ALL, 5 )
    
    self.m_checkBox_deleteCacheAfterUpload = wx.CheckBox( self.m_configurePanel, wx.ID_ANY, u"(recommended for most users)", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_checkBox_deleteCacheAfterUpload.SetValue(True) 
    fgSizer1.Add( self.m_checkBox_deleteCacheAfterUpload, 0, wx.ALL, 5 )
    
    self.m_staticText10 = wx.StaticText( self.m_configurePanel, wx.ID_ANY, u"Verbose output", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_staticText10.Wrap( -1 )
    fgSizer1.Add( self.m_staticText10, 0, wx.ALL, 5 )
    
    self.m_checkBox_verboseOutput = wx.CheckBox( self.m_configurePanel, wx.ID_ANY, u"(for debugging only)", wx.DefaultPosition, wx.DefaultSize, 0 )
    fgSizer1.Add( self.m_checkBox_verboseOutput, 0, wx.ALL, 5 )
    
    sbSizer_Basic.Add( fgSizer1, 0, wx.EXPAND, 5 )
    
    bSizer_Config.Add( sbSizer_Basic, 0, wx.EXPAND, 5 )
    
    sbSizer_Paths = wx.StaticBoxSizer( wx.StaticBox( self.m_configurePanel, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )
    
    gbSizer1 = wx.GridBagSizer( 0, 0 )
    gbSizer1.AddGrowableCol( 0 )
    gbSizer1.AddGrowableRow( 1 )
    gbSizer1.SetFlexibleDirection( wx.BOTH )
    gbSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
    
    self.m_staticText51 = wx.StaticText( self.m_configurePanel, wx.ID_ANY, u"EVE Online Paths", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_staticText51.Wrap( -1 )
    gbSizer1.Add( self.m_staticText51, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
    
    self.m_button_addPath = wx.Button( self.m_configurePanel, wx.ID_ANY, u"Add Cache Path", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_button_addPath.Enable( False )
    
    gbSizer1.Add( self.m_button_addPath, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
    
    m_listBox_evePathsChoices = [ u"C:Some_path" ]
    self.m_listBox_evePaths = wx.ListBox( self.m_configurePanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox_evePathsChoices, wx.LB_HSCROLL|wx.LB_SINGLE )
    gbSizer1.Add( self.m_listBox_evePaths, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )
    
    self.m_button_delPath = wx.Button( self.m_configurePanel, wx.ID_ANY, u"Delete Selected Cache Path", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_button_delPath.Enable( False )
    
    gbSizer1.Add( self.m_button_delPath, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
    
    sbSizer_Paths.Add( gbSizer1, 1, wx.EXPAND, 5 )
    
    bSizer_Config.Add( sbSizer_Paths, 1, wx.EXPAND, 5 )
    
    bSizer_bottom = wx.BoxSizer( wx.VERTICAL )
    
    
    bSizer_bottom.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
    
    self.m_button_applyConfig = wx.Button( self.m_configurePanel, wx.ID_ANY, u"Apply settings", wx.DefaultPosition, wx.DefaultSize, 0 )
    bSizer_bottom.Add( self.m_button_applyConfig, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
    
    bSizer_Config.Add( bSizer_bottom, 0, wx.EXPAND, 5 )
    
    self.m_configurePanel.SetSizer( bSizer_Config )
    self.m_configurePanel.Layout()
    bSizer_Config.Fit( self.m_configurePanel )
    self.m_notebook.AddPage( self.m_configurePanel, u"Configuration", False )
    
    bSizer1.Add( self.m_notebook, 1, wx.EXPAND |wx.ALL, 5 )
    
    self.SetSizer( bSizer1 )
    self.Layout()
    self.m_statusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
    
    # Connect Events
    self.m_button_applyConfig.Bind( wx.EVT_BUTTON, self.apply_configuration )
    
 
  def __del__( self ):
    pass
  
  
