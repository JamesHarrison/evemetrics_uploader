from distutils.core import setup
import py2exe

setup(
	windows=['uploader.py'],
	options={
                "py2exe":{
                        "packages": ["reverence", "sip"],
                }
        }
)
