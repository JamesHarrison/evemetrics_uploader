from distutils.core import setup
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
