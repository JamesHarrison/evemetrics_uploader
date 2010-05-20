#!/usr/bin/env python
"""
Extend Python's command line parsing (OptionParser.optparse) to support persistent configuration on disk through ConfigParser.
"""

import sys, os, shutil

from optparse import OptionParser
from ConfigParser import SafeConfigParser, DEFAULTSECT

import unittest
import tempfile

def ParseWithFile( parser, defaults = None, filename = 'settings.ini', arguments = None ):
    """
    Parse a command line and complete with data from a settings file.

    parser is an OptionParser instance that has been prepared for a parse_args() call.
    defaults is a dictionary of default values keyed by option names.

    NOTE: The parser should not have any defaults setup. Use the defaults array instead.
    If arguments is not specified, sys.argv[1:] is used.

    NOTE: Only the basic string,int,long and float types are supported, as well as store_true/store_false

    TODO: Allow specifying of options that should not be saved
"""

    # parse command line
    if ( arguments is None ):
        arguments = sys.argv[1:]
    ( options, args ) = parser.parse_args( arguments )

    # read settings
    cfp = SafeConfigParser()
    cfp.read( filename )

    # complete options with data from settings
    for option in parser.option_list:
        if ( option.dest is None ):
            continue # '--help' (special case)
        option_name = option.dest
        option_value = getattr( options, option_name )
        if ( option_value is None ):
            # see if the settings file has something
            if ( cfp.has_option( DEFAULTSECT, option_name ) ):
                # get the right type to use and assign the value
                if ( option.type == 'string' ):
                    option_value = cfp.get( DEFAULTSECT, option_name )
                elif ( option.type == 'int' ):
                    option_value = int( cfp.get( DEFAULTSECT, option_name ) )
                elif ( option.type == 'long' ):
                    option_value = int( cfp.get( DEFAULTSECT, option_name ) )
                elif ( option.type == 'float' ):
                    option_value = float( cfp.get( DEFAULTSECT, option_name ) )
                else:
                    if ( option.action == 'store_true' or option.action == 'store_false' ):
                        option_value = ( cfp.get( DEFAULTSECT, option_name ) == 'True' )
                    else:
                        raise Exception( 'Option \'%s\' uses an unsupported type \'%s\'' % ( option_name, option.type ) )
                setattr( options, option_name, option_value )
            elif ( ( not ( defaults is None ) ) and defaults.has_key( option_name ) ):
                # we know a default value to apply
                setattr( options, option_name, defaults[ option_name ] )
        else:
            # a value was passed on the command line
            if ( ( defaults is None ) or ( not defaults.has_key( option_name ) ) ):
                # no default is known for that value, always save to the config file
                cfp.set( DEFAULTSECT, option_name, str( option_value ) )
            else:
                if ( defaults[ option_name ] != option_value ):
                    # save a different value than the default
                    cfp.set( DEFAULTSECT, option_name, str( option_value ) )
                else:
                    # explicitely passing the default value means we should not store it
                    cfp.remove_option( DEFAULTSECT, option_name ) # will return False if no option exist

    # write out the updated configuration
    cfp.write( file( filename, 'w' ) )

    return ( options, args )

def SaveToFile( options, parser, defaults = None, filename = 'settings.ini' ):
    """"Save back to file a set of options that have been modified by the application"""
    # read settings
    cfp = SafeConfigParser()
    cfp.read( filename )

    # complete options with data from settings
    for option in parser.option_list:
        if ( option.dest is None ):
            continue # '--help' (special case)
        option_name = option.dest
        option_value = getattr( options, option_name )
        if ( option_value is None ):
            continue
        # a value was passed on the command line
        if ( ( defaults is None ) or ( not defaults.has_key( option_name ) ) ):
            # no default is known for that value, always save to the config file
            cfp.set( DEFAULTSECT, option_name, str( option_value ) )
        else:
            if ( defaults[ option_name ] != option_value ):
                # save a different value than the default
                cfp.set( DEFAULTSECT, option_name, str( option_value ) )
            else:
                # explicitely passing the default value means we should not store it
                cfp.remove_option( DEFAULTSECT, option_name ) # will return False if no option exist
    # write out the updated configuration
    cfp.write( file( filename, 'w' ) )        

class Test( unittest.TestCase ):
    """Unit Tests"""

    def setUp( self ):
        self.directory = tempfile.mkdtemp()

    def tearDown( self ):
        shutil.rmtree( self.directory )

    def test_NoSettings( self ):
        """Verify parsing with no settings"""
        p = OptionParser()
        p.add_option( '-t', '--test', dest = 'test', help = 'test string' )
        args = [ '-t', 'bar' ]
        ( options, args ) = ParseWithFile( p, None, os.path.join( self.directory, 'nosettings.ini' ), args )
        self.failUnless( options.test == 'bar' )

    def test_FromSettings( self ):
        """Verify getting a value from settings"""
        p = OptionParser()
        p.add_option( '-t', '--test', dest = 'test', help = 'test string' )
        settings_name = os.path.join( self.directory, 'settings.ini' )
        settings = file( settings_name, 'w' )
        cfp = SafeConfigParser()
        cfp.set( DEFAULTSECT, 'test', 'foo' )
        cfp.write( settings )
        settings.close()
        args = []
        ( options, args ) = ParseWithFile( p, None, settings_name, args )
        self.failUnless( options.test == 'foo' )

    def test_Defaults( self ):
        """Verify that defaults work"""
        p = OptionParser()
        p.add_option( '-d', '--default', dest = 'default', type = 'int', help = 'will be assigned a default value' )
        args = []
        defaults = { 'default' : 10 }
        ( options, args ) = ParseWithFile( p, defaults, os.path.join( self.directory, 'nosettings.ini' ), args )
        self.failUnless( options.default == 10 )
    
    def test_CorrectType( self ):
        """Verify that types are restored properly from settings"""
        p = OptionParser()
        p.add_option( '-i', '--int', dest = 'intval', type = 'int', help = 'int value' )
        p.add_option( '-f', '--float', dest = 'floatval', type = 'float', help = 'float value' )
        settings_name = os.path.join( self.directory, 'settings.ini' )
        settings = file( settings_name, 'w' )
        cfp = SafeConfigParser()
        cfp.set( DEFAULTSECT, 'intval', '10' )
        cfp.set( DEFAULTSECT, 'floatval', str( 3.14 ) )
        cfp.write( settings )
        settings.close()
        args = []
        ( options, args ) = ParseWithFile( p, None, settings_name, args )
        self.failUnless( options.intval == 10 )
        self.failUnless( options.floatval == 3.14 )

    def test_SaveAndRestore( self ):
        """Verify a value used is saved and restored properly"""
        p = OptionParser()
        p.add_option( '-s', '--set', dest = 'key' )
        args = [ '-s', 'save and restore' ]
        settings_name = os.path.join( self.directory, 'save_and_restore.ini' )
        settings = file( settings_name, 'w' )
        ParseWithFile( p, None, settings_name, args )
        # read again with no args
        p2 = OptionParser()
        p2.add_option( '-s', '--set', dest = 'key' )
        ( options, args ) = ParseWithFile( p2, None, settings_name, [] )
        self.failUnless( options.key == 'save and restore' )

    def test_DefaultOverride( self ):
        """Verify that a value with a default can be permanently modified"""
        p = OptionParser()
        p.add_option( '-d', '--default', dest = 'default', type = 'int', help = 'will be assigned a default value' )
        defaults = { 'default' : 10 }
        args = [ '-d', '20' ]
        ParseWithFile( p, defaults, os.path.join( self.directory, 'defaults_override.ini' ), args )
        # read again with no args
        p2 = OptionParser()
        p2.add_option( '-d', '--default', dest = 'default', type = 'int', help = 'will be assigned a default value' )
        ( options, args ) = ParseWithFile( p2, defaults, os.path.join( self.directory, 'defaults_override.ini' ), [] )
        self.failUnless( options.default == 20 )

    def test_DefaultNonStick( self ):
        """Verify that values at their default are not saved so defaults can be changed"""
        p = OptionParser()
        p.add_option( '-d', '--default', dest = 'default', type = 'int', help = 'will be assigned a default value' )
        defaults = { 'default' : 10 }
        args = [ '-d', '10' ]
        ParseWithFile( p, defaults, os.path.join( self.directory, 'defaults_notsaved.ini' ), args )
        # read again with different default and no args
        p2 = OptionParser()
        p2.add_option( '-d', '--default', dest = 'default', type = 'int', help = 'will be assigned a default value' )
        new_defaults = { 'default' : 20 }
        ( options, args ) = ParseWithFile( p2, new_defaults, os.path.join( self.directory, 'defaults_notsaved.init' ), [] )
        self.failUnless( options.default == 20 )

    def test_DefaultReset( self ):
        """Verify that a default override can be 'reset' by passing the default value again"""
        # extending past another test ..
        self.test_DefaultOverride()
        # default set at 20 rather than 10, saved to defaults_override.ini
        # now pass a default of 10 and an argument of 10
        p = OptionParser()
        p.add_option( '-d', '--default', dest = 'default', type = 'int', help = 'will be assigned a default value' )
        defaults = { 'default' : 10 }
        args = [ '-d', '10' ]
        fn = os.path.join( self.directory, 'defaults_override.ini' )
        ParseWithFile( p, defaults, fn, args )
        # verify that no value is stored in the ini anymore
        cfp = SafeConfigParser()
        cfp.read( fn )
        self.failIf( cfp.has_option( DEFAULTSECT, 'default' ) )

class TestBool( unittest.TestCase ):
    """Test store_true/store_false usage"""

    def setUp( self ):
        self.directory = tempfile.mkdtemp()

    def tearDown( self ):
        shutil.rmtree( self.directory )

    def test_Bool( self ):
        """Yes/No flag to same destination with a default value."""
        p = OptionParser()
        p.add_option( '-y', '--yes', action = 'store_true', dest = 'v' )
        p.add_option( '-n', '--no', action = 'store_false', dest = 'v' )
        defaults = { 'v' : True }
        args = [ '-n' ]
        ( options, args ) = ParseWithFile( p, defaults, 'booltest.ini', args )
        self.failUnless( not options.v )
        # verify store/restore
        p2 = OptionParser()
        p2.add_option( '-y', '--yes', action = 'store_true', dest = 'v' )
        p2.add_option( '-n', '--no', action = 'store_false', dest = 'v' )
        ( options, args ) = ParseWithFile( p2, defaults, 'booltest.ini', [] )
        self.failUnless( not options.v )
        # and the other way
        p3 = OptionParser()
        p3.add_option( '-y', '--yes', action = 'store_true', dest = 'v' )
        p3.add_option( '-n', '--no', action = 'store_false', dest = 'v' )
        ( options, args ) = ParseWithFile( p3, defaults, 'booltest.ini', [ '-y' ] )
        self.failUnless( options.v )

if ( __name__ == '__main__' ):
    unittest.main()
