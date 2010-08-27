from reverence import blue 


class Processor( object ):
    def __init__( self, upload_client, eve_path ):
        self.upload_client = upload_client
        self.eve_path = eve_path
        #eve = blue.EVE( eve_path )
        #self.reverence = eve.getcachemgr()

    def OnNewFile( self, pathname ):
        try:
            if ( pathname.__class__ == QtCore.QString ):
                pathname = str( pathname )
            print 'OnNewFile: %s' % pathname
            if ( os.path.splitext( pathname )[1] != '.cache' ):
                logging.debug( 'Not a .cache, skipping' )
                return
            try:
                parsed_data = parser.parse( pathname )
            except IOError:
                # I was retrying initially, but some files are deleted before we get a chance to parse them,
                # which is what's really causing this
                logging.warning( 'IOError exception, skipping' )
                return
            if ( parsed_data is None ):
                logging.debug( 'No data parsed' )
                return
            t = self.reverence.invtypes.Get( parsed_data[2] )
            
            logging.debug( 'Call %s, regionID %d, typeID %d' % ( parsed_data[0], parsed_data[1], parsed_data[2] ) )

            ret = self.upload_client.send(parsed_data)
            if ( ret ):
                if ( parsed_data[0] == 'GetOldPriceHistory' ):
                    logging.info( 'Uploaded price history for %s in %s' % (t.name, REGION_MAP.get(parsed_data[1], 'Unknown') ) )
                else:
                    logging.info( 'Uploaded orders for %s in %s' % (t.name, REGION_MAP.get(parsed_data[1], 'Unknown') ) )
                logging.debug( 'Removing cache file %s' % pathname )
                os.remove( pathname )
            else:
                logging.error( 'Could not upload file')
                # We should manage some sort of backlog if evemetrics is down
        except:
            traceback.print_exc()
        else:
            print ret