from pyfurstream import api
from pyfurstream.decorators import cached_property

class User:
    def __init__(self, name=None):
        self.name = name
        
    @cached_property(ttl=600)
    def _summary(self):
        if api().developer:
            return api().call('IUsers', 'GetUserSummaries', users=self.name)['users'][0]
        else:
            return api().call('IUsers', 'GetUserSummary')
        
    @property
    def username(self):
        return self._summary['username']
    
    @property
    def email(self):
        try:
            return self._summary['email']
        except KeyError:
            return None
    
    @property
    def blurb(self):
        return self._summary['blurb']
    
    @property
    def website(self):
        return self._summary['website']
    
    @property
    def banned(self):
        return self._summary['banned']
    
    @property
    def joined(self):
        return self._summary['joined']
    
    @property
    def avatar(self):
        return self._summary['avatar']
        
    @property
    def inkbunny(self):
        return self._summary['inkbunny']
        
    @property
    def weasyl(self):
        return self._summary['weasyl']
        
    @property
    def sofurry(self):
        return self._summary['sofurry']
        
    @property
    def furaffinity(self):
        return self._summary['furaffinity']
    
    