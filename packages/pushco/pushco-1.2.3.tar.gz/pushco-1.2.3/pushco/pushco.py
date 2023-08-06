import urllib
import urllib2

class Pushco(object):
    
    
    def __init__(self, api_key, api_secret, message, url=None, latitude=None, longitude=None, view_type = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.message = message
        self.url = url
        self.latitude = latitude
        self.longitude = longitude
        self.view_type = view_type
        
    def push(self):
        params = {
                  'api_key':self.api_key,
                  'api_secret':self.api_secret,
                  'message':self.message
                  }
        if self.url:    
            params['url']= self.url
            params['view_type']= 1
        elif self.latitude:
            params['latitude']=self.latitude
            params['longitude']=self.longitude
            params['view_type']= 2
            
        print self.url
        req = urllib2.Request('https://api.push.co/1.0/push', urllib.urlencode(params))
        try:
            response = urllib2.urlopen(req)
            return response.getcode()
        except urllib2.URLError, e:
            if e.code == 422:
                return ' %s Message too long' %e.code
            if e.code == 401:
                return  '%s - Not authorised' %e.code
            if e.code == 500:
                return  '%s - Internal server error' %e.code
            else:
                return  '%s - HTTP error' %e.code
        
        
        