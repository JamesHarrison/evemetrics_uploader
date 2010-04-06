# python modules
import sys, os, traceback
from optparse import OptionParser
# python extras
import pyinotify
# local modules
from evemetrics import parser, uploader

class HandleEvents(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        try:
            print 'New file: %s' % event.pathname
            if ( os.path.splitext( event.pathname )[1] != '.cache' ):
                return
            parsed_data = parser.parse(event.pathname)
            if ( parsed_data is None ):
                return
            print 'Call %s, regionID %d, typeID %d' % ( parsed_data[0], parsed_data[1], parsed_data[2] )
            ret = upload_client.send(parsed_data)
        except:
            traceback.print_exc()
        else:
            print ret

if ( __name__ == '__main__' ):
    p = OptionParser()
    p.add_option( '-t', '--token', dest = 'token', help = 'EVE Metrics application token - see http://www.eve-metrics.com/downloads' )
    p.add_option( '-p', '--path', dest = 'path', default = r'C:\Users\James\AppData\Local\CCP\EVE\c_program_files_(x86)_ccp_eve_-_5_tranquility\cache', help = 'EVE cache path' )
    ( options, args ) = p.parse_args()

    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CLOSE_WRITE
    upload_client = uploader.Uploader()
    upload_client.set_token( options.token )

    notifier = pyinotify.ThreadedNotifier(wm, HandleEvents())
    notifier.start()
    
    # On windows this path would be C:\Users\James\AppData\Local\CCP\EVE\c_program_files_(x86)_ccp_eve_-_5_tranquility\cache\ 
    # the folder should contain a MachoNet folder (plus others)
    # if you run multiple clients, just call wm.add_watch some more.
    wdd = wm.add_watch( options.path, mask, rec = True )



