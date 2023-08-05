from pyfurstream import api
from pyfurstream.decorators import cached_property

class Stream:
    def __init__(self, name=None):
	    self.name = name
        
    @cached_property(ttl=600)
    def _summary(self):
        if api().developer:
            return api().call('IStreams', 'GetStreamSummaries', streams=self.name)['streams'][0]
        else:
            return api().call('IStreams', 'GetStreamSummary')
            
    @property
    def name(self):
        return self._summary['name']
    
    @property
    def title(self):
        return self._summary['title']
        
    @property
    def online(self):
        return self._summary['online']
    
    @property
    def viewers(self):
        return self._summary['viewers']
    
    @property
    def icon(self):
        return self._summary['icon']
        
    @property
    def genre(self):
        return self._summary['genre']
        
    @property
    def rating(self):
        return self._summary['rating']

    @property
    def private(self):
        return self._summary['private']
        
    @property
    def description(self):
        return self._summary['description']
        
    @property
    def status_img(self):
        return self._summary['status_img']