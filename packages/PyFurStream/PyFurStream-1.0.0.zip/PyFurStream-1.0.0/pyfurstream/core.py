import requests
import os

class APIConnection:
    def __init__(self, apikey=None, access=1):
        self.apikey = apikey
        self.access = access
        
    def call(self, interface, method, **params):
        for param in params:
            if type(params[param]) is list:
                params[param] = ','.join(params[param])
            elif type(params[param]) is bool:
                if params[param]:
                    params[param] = 1
                else:
                    params[param] = 0
        params['key'] = self.apikey
        response = requests.request('GET', 'https://furstre.am/API/v2/{0}/{1}'.format(interface, method), params=params)
        if response.status_code == 200:
            return response.json()
        else:    
            raise ApiException(response.status_code)
            
    @property
    def developer(self):
        return self.access == 1
            
class ApiException(Exception):
    def __init__(self, status_code):
        if status_code == 403:
            self.message = "API Key invalid"
        elif status_code == 400:
            self.message = "Malformed request"
        else:
            self.message = "Could not connect to FurStream API"

    def __str__(self):
        return self.message
        
__api__ = None

def api():
    global __api__
    if not __api__:
        __api__ = APIConnection(os.environ.get('FURSTREAM_APIKEY', None))
    return __api__
    
def configure(api_key, **params):
    global __api__
    __api__ = APIConnection(api_key, **params)
    return __api__
    