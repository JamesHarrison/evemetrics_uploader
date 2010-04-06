import httplib
import urllib
import hashlib

class Uploader:
  def __init__(self):
    self.token = ''
    self.developer_key = '396101116843ECC01FCCE'
    

  # Sets the application token for this user
  def set_token(self,token):
    self.token = token
    
  # Sends the passed result of a file parse to EVE Metrics.
  def send(self,data):
    target = ('/api/upload_orders.xml' if data[0] == 'GetOrders' else '/api/upload_history.xml')
    # Compute the hash of the body
    hasher = hashlib.sha1()
    hasher.update(self.developer_key)
    hasher.update(data[4])
    body_hash = hasher.hexdigest()
    # Fire off a HTTP request
    conn = httplib.HTTPConnection("eve-metrics.com")
    conn.request("POST", target, urllib.urlencode({'token':self.token, 'developer_key':self.developer_key,'version':'2.0','hash':body_hash,'generated_at':data[4],'log': data[3]}), {'Content-Type': 'application/x-www-form-urlencoded'} )
    response = conn.getresponse()
    print response.status, response.reason
    print response.read()
    conn.close()
    return response.status == 200
