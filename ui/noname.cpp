///////////////////////////////////////////////////////////////////////////
// C++ code generated with wxFormBuilder (version May  4 2010)
// http://www.wxformbuilder.org/
//
// PLEASE DO "NOT" EDIT THIS FILE!
///////////////////////////////////////////////////////////////////////////

#include "noname.h"

///////////////////////////////////////////////////////////////////////////

EMUMainFrame::EMUMainFrame( wxWindow* parent, wxWindowID id, const wxString& title, const wxPoint& pos, const wxSize& size, long style ) : wxFrame( parent, id, title, pos, size, style )
{
	this->SetSizeHints( wxDefaultSize, wxDefaultSize );
	
	wxBoxSizer* bSizer1;
	bSizer1 = new wxBoxSizer( wxVERTICAL );
	
	m_notebook = new wxNotebook( this, wxID_ANY, wxDefaultPosition, wxDefaultSize, 0 );
	m_statusPanel = new wxPanel( m_notebook, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxTAB_TRAVERSAL );
	wxGridSizer* gSizer1;
	gSizer1 = new wxGridSizer( 1, 1, 0, 0 );
	
	m_textCtrl_log = new wxTextCtrl( m_statusPanel, wxID_ANY, wxEmptyString, wxDefaultPosition, wxDefaultSize, wxTE_AUTO_URL|wxTE_MULTILINE|wxTE_READONLY|wxHSCROLL );
	gSizer1->Add( m_textCtrl_log, 0, wxALL|wxEXPAND, 5 );
	
	m_statusPanel->SetSizer( gSizer1 );
	m_statusPanel->Layout();
	gSizer1->Fit( m_statusPanel );
	m_notebook->AddPage( m_statusPanel, wxT("Status"), true );
	m_configurePanel = new wxPanel( m_notebook, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxTAB_TRAVERSAL );
	wxFlexGridSizer* fgSizer1;
	fgSizer1 = new wxFlexGridSizer( 6, 2, 0, 0 );
	fgSizer1->SetFlexibleDirection( wxBOTH );
	fgSizer1->SetNonFlexibleGrowMode( wxFLEX_GROWMODE_SPECIFIED );
	
	m_staticText1 = new wxStaticText( m_configurePanel, wxID_ANY, wxT("Application Token"), wxDefaultPosition, wxDefaultSize, 0 );
	m_staticText1->Wrap( 0 );
	fgSizer1->Add( m_staticText1, 0, wxALL, 5 );
	
	m_textCtrl_appToken = new wxTextCtrl( m_configurePanel, wxID_ANY, wxEmptyString, wxDefaultPosition, wxDefaultSize, 0 );
	fgSizer1->Add( m_textCtrl_appToken, 0, wxALL, 5 );
	
	
	fgSizer1->Add( 0, 0, 1, wxEXPAND, 5 );
	
	m_hyperlink1 = new wxHyperlinkCtrl( m_configurePanel, wxID_ANY, wxT("Don't know your token?"), wxT("http://www.eve-metrics.com/downloads/"), wxDefaultPosition, wxDefaultSize, wxHL_DEFAULT_STYLE );
	fgSizer1->Add( m_hyperlink1, 0, wxALL, 5 );
	
	m_staticText2 = new wxStaticText( m_configurePanel, wxID_ANY, wxT("Delete cache\nfile after upload"), wxDefaultPosition, wxDefaultSize, 0 );
	m_staticText2->Wrap( 0 );
	fgSizer1->Add( m_staticText2, 0, wxALL, 5 );
	
	m_checkBox_deleteCacheAfterUpload = new wxCheckBox( m_configurePanel, wxID_ANY, wxT("(recommended for most users)"), wxDefaultPosition, wxDefaultSize, 0 );
	fgSizer1->Add( m_checkBox_deleteCacheAfterUpload, 0, wxALL, 5 );
	
	m_staticText5 = new wxStaticText( m_configurePanel, wxID_ANY, wxT("EVE Online Paths"), wxDefaultPosition, wxDefaultSize, 0 );
	m_staticText5->Wrap( 0 );
	fgSizer1->Add( m_staticText5, 0, wxALL, 5 );
	
	m_listBox_evePaths = new wxListBox( m_configurePanel, wxID_ANY, wxDefaultPosition, wxDefaultSize, 0, NULL, wxLB_HSCROLL|wxLB_SINGLE );
	m_listBox_evePaths->Append( wxT("C:Some_path") );
	m_listBox_evePaths->Append( wxT("/home/james/some_path/") );
	fgSizer1->Add( m_listBox_evePaths, 0, wxALL|wxEXPAND, 5 );
	
	
	fgSizer1->Add( 0, 0, 1, wxEXPAND, 5 );
	
	m_button_addPath = new wxButton( m_configurePanel, wxID_ANY, wxT("Add Cache Path"), wxDefaultPosition, wxDefaultSize, 0 );
	fgSizer1->Add( m_button_addPath, 0, wxALL, 5 );
	
	
	fgSizer1->Add( 0, 0, 1, wxEXPAND, 5 );
	
	m_button_delPath = new wxButton( m_configurePanel, wxID_ANY, wxT("Delete Selected Cache Path"), wxDefaultPosition, wxDefaultSize, 0 );
	fgSizer1->Add( m_button_delPath, 0, wxALL, 5 );
	
	m_configurePanel->SetSizer( fgSizer1 );
	m_configurePanel->Layout();
	fgSizer1->Fit( m_configurePanel );
	m_notebook->AddPage( m_configurePanel, wxT("Configuration"), false );
	
	bSizer1->Add( m_notebook, 1, wxEXPAND | wxALL, 5 );
	
	this->SetSizer( bSizer1 );
	this->Layout();
	m_statusBar = this->CreateStatusBar( 1, wxST_SIZEGRIP, wxID_ANY );
}

EMUMainFrame::~EMUMainFrame()
{
}
