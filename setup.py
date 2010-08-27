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
                'argv_emulation' : True, # no idea what that is
                'packages' : [ 'reverence' ],
                }
            }
        )
    # pulls in too much cruft still, finish the job
    import os, subprocess, shutil
    rmdirs = subprocess.Popen( [ 'find', 'dist/uploader.app', '-name', '*debug*' ], stdout = subprocess.PIPE )
    ( out, err ) = rmdirs.communicate()
    out = out.strip()
    for p in out.split('\n'):
        if ( len( p ) == 0 ):
            continue
        print( 'Removing %s' % p )
        if ( os.path.isdir( p ) ):
            shutil.rmtree( p )
        else:
            os.unlink( p )
    # print the size, since it's kinda crazy
    subprocess.call( [ 'du', '-h', '-d', '0', 'dist/uploader.app' ] )
    # considered using lipo to thin out multi arch binaries, but it turned out there were very few of them and they were small

            
