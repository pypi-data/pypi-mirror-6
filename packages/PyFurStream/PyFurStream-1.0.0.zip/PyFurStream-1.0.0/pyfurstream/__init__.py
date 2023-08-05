from pyfurstream.core import APIConnection, api, configure
from pyfurstream.users import User
from pyfurstream.streams import Stream

import time

__version__ = "1.0.0"

def get_user_summaries(users):
        '''
        Returns the list of user objects for the given list of usernames
        Note: The list of objects is not guaranteed (nor likely) to be
        in the same order in which the usernames are given
        '''
        _users = api().call('IUsers', 'GetUserSummaries', users=users)
        userlist = []
        for _user in _users['users']:
            user = User(_user['username'])
            user._cache = {}
            user._cache['_summary'] = (_user, time.time())
            userlist.append(user)
        return userlist
        
        
def get_stream_summaries(streams):
        '''
        Returns the list of stream objects for the given list of stream names
        Note: The list of objects is not guaranteed (nor likely) to be
        in the same order in which the stream names are given
        '''
        _streams = api().call('IStreams', 'GetStreamSummaries', streams=streams)
        streamlist = []
        for _stream in _streams['streams']:
            stream = Stream(_stream['name'])
            stream._cache = {}
            stream._cache['_summary'] = (_stream, time.time())
            streamlist.append(stream)
        return streamlist


def get_live_streams():
    '''
    Returns a list of stream objects representing all currently live streams
    '''
    streams = api().call('IStreams', 'GetLiveStreams')['streams']
    return get_stream_summaries(streams)
    

def get_best_server(address):
    return api().call('IFurStream', 'GetBestServer', address=address)