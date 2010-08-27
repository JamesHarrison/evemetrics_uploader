///////////////////////////////////////////////////////////////////////////
// C++ code generated with wxFormBuilder (version May  4 2010)
// http://www.wxformbuilder.org/
//
// PLEASE DO "NOT" EDIT THIS FILE!
///////////////////////////////////////////////////////////////////////////

#ifndef __noname__
#define __noname__

#include <wx/string.h>
#include <wx/textctrl.h>
#include <wx/gdicmn.h>
#include <wx/font.h>
#include <wx/colour.h>
#include <wx/settings.h>
#include <wx/sizer.h>
#include <wx/panel.h>
#include <wx/bitmap.h>
#include <wx/image.h>
#include <wx/icon.h>
#include <wx/stattext.h>
#include <wx/hyperlink.h>
#include <wx/checkbox.h>
#include <wx/listbox.h>
#include <wx/button.h>
#include <wx/notebook.h>
#include <wx/statusbr.h>
#include <wx/frame.h>

///////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////
/// Class EMUMainFrame
///////////////////////////////////////////////////////////////////////////////
class EMUMainFrame : public wxFrame 
{
	private:
	
	protected:
		wxNotebook* m_notebook;
		wxPanel* m_statusPanel;
		wxTextCtrl* m_textCtrl_log;
		wxPanel* m_configurePanel;
		wxStaticText* m_staticText1;
		wxTextCtrl* m_textCtrl_appToken;
		
		wxHyperlinkCtrl* m_hyperlink1;
		wxStaticText* m_staticText2;
		wxCheckBox* m_checkBox_deleteCacheAfterUpload;
		wxStaticText* m_staticText5;
		wxListBox* m_listBox_evePaths;
		
		wxButton* m_button_addPath;
		
		wxButton* m_button_delPath;
		wxStatusBar* m_statusBar;
	
	public:
		
		EMUMainFrame( wxWindow* parent, wxWindowID id = wxID_ANY, const wxString& title = wxT("EVE Metrics Uploader 2"), const wxPoint& pos = wxDefaultPosition, const wxSize& size = wxSize( 350,400 ), long style = wxCAPTION|wxCLOSE_BOX|wxMINIMIZE_BOX|wxRESIZE_BORDER|wxSYSTEM_MENU|wxTAB_TRAVERSAL );
		~EMUMainFrame();
	
};

#endif //__noname__
