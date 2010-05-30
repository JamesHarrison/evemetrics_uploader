import platform

from distutils.core import setup

if ( platform.system() == 'Windows' ):
    import py2exe
    setup(
	console=['uploader.py'],
	zipfile = None,
	options={
            "py2exe":{
                "packages": ["reverence", "sip"],
                'bundle_files': 1
                }
            }
        )
elif ( platform.system() == 'Darwin' ):
    import py2app
    setup(
        app = [ 'uploader.py' ],
        options = {
            'py2app' : {
                'packages' : [ 'PyQt4', 'reverence' ]
                }
            }
        )
