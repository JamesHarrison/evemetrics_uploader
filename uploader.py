from evemetrics import parser,uploader
import pyinotify

wm = pyinotify.WatchManager()
mask = pyinotify.IN_CLOSE_WRITE
upload_client = uploader.Uploader()

upload_client.set_token("PUT YOUR TOKEN HERE")

class HandleEvents(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        print "Creating:", event.pathname
        parsed_data = parser.parse(event.pathname)
        print "Call "+parsed_data[0]+", regionID "+parsed_data[1]+", typeID "+parsed_data[2]
        print upload_client.send(parsed_data)

notifier = pyinotify.ThreadedNotifier(wm, HandleEvents())
notifier.start()
# On windows this path would be C:\Users\James\AppData\Local\CCP\EVE\c_program_files_(x86)_ccp_eve_-_5_tranquility\cache\ 
# the folder should contain a MachoNet folder (plus others)
# if you run multiple clients, just call wm.add_watch some more.
wdd = wm.add_watch('path-to-eve-cache', mask, rec=True)


