import httplib, urllib, hashlib, logging
from xml.dom.minidom import parse, parseString
import pprint
import time
logger = logging.getLogger('emu')

class Uploader:
  def __init__(self):
    self.token = ''
    self.developer_key = '396101116843ECC01FCCE'    

  # Sets the application token for this user
  def set_token(self,token):
    self.token = token
    
  # Sends the passed result of a file parse to EVE Metrics.
  def send(self,data, detail = False):
    target = ('/api/upload_orders.xml' if data[0] == 'GetOrders' else '/api/upload_history.xml')
    # Compute the hash of the body
    hasher = hashlib.sha1()
    hasher.update(self.developer_key)
    hasher.update(data[4])
    body_hash = hasher.hexdigest()
    # Fire off a HTTP request
    conn = httplib.HTTPConnection("eve-metrics.com")
    conn.request( "POST",
                  target,
                  urllib.urlencode( {
          'token' : self.token,
          'developer_key' : self.developer_key,
          'version' : '2.0',
          'hash' : body_hash,
          'generated_at' : data[4],
          'log' : data[3]
          } ),
                  {
        'Content-Type': 'application/x-www-form-urlencoded'
        } )
    response = conn.getresponse()
    logger.debug("%s, %s" % (response.status, response.reason))
    if detail:
      try:
        parser = parseString(response.read())
        conn.close()
        code = parser.getElementsByTagName("code")
        if code.length > 0:
          response = parser.getElementsByTagName("resp")[0]
          return (int(code[0].firstChild.data), (response.firstChild.data if response.firstChild else ''))
          
        error = parser.getElementsByTagName("error")
        if error.length > 0:
          attributes = parser.getElementsByTagName("error")[0].attributes
          return (int(attributes.item(1).value), attributes.item(0).value)
      except:
        logger.exception('Error parsing HTTPResponse')
        return (403, 'Could not parse server response.')
    else:
      conn.close()
      return response.status == 200
    
  # Checks the application token for validility
  def check_token(self):
    # Fire off a HTTP request
    conn = httplib.HTTPConnection("eve-metrics.com")
    conn.request( "POST",
                  '/api/check_token.xml',
                  urllib.urlencode( {
                    'token' : self.token,
                    'developer_key' : self.developer_key,
                    'version' : '2.0',
                  } ),
                  {
                  'Content-Type': 'application/x-www-form-urlencoded'
                  } )
    response = conn.getresponse()
    logger.debug("%s, %s" % (response.status, response.reason))
    try:
      node = parseString(response.read()).getElementsByTagName("token")[0]
      attributes = node.attributes
      conn.close()
      if attributes.length == 0:
        return (False, '')
      else:
        return ((attributes.item(0).value == 'ok'), node.firstChild.data)
    except:
      logger.exception('Error parsing HTTPResponse')
      return (False, 'error')
    