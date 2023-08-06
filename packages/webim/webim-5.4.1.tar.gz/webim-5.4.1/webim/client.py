#!/usr/bin/env python
#coding: utf-8

"""
python webim client

Overview
========

See U{the Webim homepage<https://www.github.com/webim>} for more about webim.

Usage summary
=============

This should give you a feel for how this module operates::

    import webim 
    endpoint = {'uid': 'uid1', 'nick': 'user1', 'presence': 'online', 'show': 'available', 'status': ''}
    c = webim.Client(endpoint, 'domain', 'apikey', host='127.0.0.1', port = 8000)
    c.online(['uid1','uid2','uid3'], ['room1','room2','room3'])
    c.offline()

Detailed Documentation
======================

More detailed documentation is available in the L{Client} class.
"""

APIVSN = 'v5'

try:
    import json
except ImportError:
    import simplejson as json

import time
import base64
import urllib
import httplib
import hashlib

# ==============================================================================
# Helpers
# ==============================================================================
def encode_utf8(data_dict):
    for key, value in data_dict.iteritems():
        if isinstance(value, unicode):
            data_dict[key] = value.encode('utf8')
    return data_dict

class WebimException(Exception):
    def __init__(self, status, reason, error):
        self.args = (status, reason, error)
        self.status = status
        self.reason = reason
        self.error = error

# ==============================================================================
# Client
# ==============================================================================    
class Client:
    
    def __init__(self, endpoint, domain, apikey,
                 ticket=None, host = 'localhost', port=8000, timeout=15):
        """
        Create a new Client object with the given host and port

        @param endpoint: endpoint
        @param host: host
        @param port: port
        """
        self.endpoint = endpoint
        self.domain = domain
        self.apikey = apikey
        self.ticket = ticket
        self.host = host
        self.port = port
        self.timeout = timeout
        
    def online(self, buddies, rooms):
        """
        Client online
        """
        reqdata = self._reqdata
        reqdata.update({
            'buddies': ','.join(buddies),
            'rooms': ','.join(rooms),
            'name': self.endpoint['id'],
            'nick': self.endpoint['nick'],
            'show': self.endpoint['show'],
            'status': self.endpoint['status']
        })
        respdata = self._httpost('/presences/online', reqdata)
        self.ticket = respdata['ticket']
        conn = {
            'ticket': self.ticket,
            'domain': self.domain, 
            'server': respdata['jsonpd'],
            'jsonpd': respdata['jsonpd']
        }
        if 'websocket' in respdata:
            conn['websocket'] = respdata['websocket']
        if 'mqtt' in respdata:
            conn['mqtt'] = respdata['mqtt']
        return {
            'success': True,
            'connection': conn,
            'presences': respdata['presences']
        }

    def show(self, show, status=None):
        """
        Send Presence
        """
        reqdata = self._reqdata
        reqdata.update({
            'type': 'show',
            'nick': self.endpoint['nick'],   
            'show': show
        })
        if status: reqdata['status'] = status
        return self._httpost('/presences/show', reqdata)

    def offline(self):
        """
        Client offline
        """
        return self._httpost('/presences/offline', self._reqdata)

    def message(self, message):
        """
        Send Message
        """
        reqdata = self._reqdata
        reqdata.update({
            'nick': self.endpoint['nick'],
            'type': message['type'],
            'to': message['to'],
            'body': message['body'],
            'style': message['style'],
            'timestamp': message['timestamp']
        })
        if 'from' in message: 
            reqdata['from'] = message['from']
        return self._httpost('/messages', reqdata)

    def status(self, status):
        """
        Send Status
        """
        reqdata = self._reqdata
        reqdata.update({
            'nick': self.endpoint['nick'],
            'to': status['to'],
            'show': status['show']
        })
        return self._httpost('/statuses', reqdata)

    def presences(self, ids):
        """
        Read presences
        """
        reqdata = self._reqdata
        reqdata.update({
            'ids': ",".join(ids)
        })
        return self._httpget("/presences", reqdata)

    def members(self, room):
        """
        Read room members
        """
        reqdata = self._reqdata
        reqdata.update({
            'room': room 
        })
        return self._httpget('/rooms/' + room + '/members', reqdata)
            
    def join(self, room):
        """
        Join room
        """
        reqdata = self._reqdata
        reqdata.update({
            'nick': self.endpoint['nick'],
            'room': room
        })
        return self._httpost('/rooms/' + room + '/join', reqdata)
            
    def leave(self, room):
        """
        Leave room 
        """
        reqdata = self._reqdata
        reqdata.update({
            'nick': self.endpoint['nick'],
            'room': room
        })
        return self._httpost('/rooms/' + room + '/leave', reqdata)
        
    @property
    def _reqdata(self):
        data = {
            'version': APIVSN,
            'domain': self.domain
        }
        if self.ticket is not None: 
            data['ticket'] = self.ticket
        return data

    def _httpget(self, path, params=None):
        """
        HTTP GET
        """
        url = self._apiurl(path)
        if __debug__: 
            print 'GET.url:', url
            print 'GET.params: ', params
        if params is not None: 
            url += "?" + urllib.urlencode(encode_utf8(params))
        return self._httprequest('GET', url)

    def _httpost(self, path, data):
        """
        HTTP POST
        """
        url = self._apiurl(path)
        if __debug__: 
            print 'POST.url:', url
            print 'POST.data:', data
        data = urllib.urlencode(encode_utf8(data))
        return self._httprequest('POST', url, data)

    def _httprequest(self, method, url, data=None):
        content = None
        try:
            auth = base64.b64encode(self.domain+':'+self.apikey)
            headers = {'Authorization': 'Basic ' + auth}
            connection = httplib.HTTPConnection(self.host, self.port, timeout=self.timeout)
            connection.request(method, url, data, headers) 
            response = connection.getresponse()
            status = response.status
            if status / 100 == 2:
                content = response.read()
                if __debug__: 
                    print method + '.response:'
                    print content
                if not url.startswith('/'+APIVSN+'/packets'): 
                    content = json.loads(content)
            else:
                raise WebimException(status, response.reason, response.read())
        finally:
            if connection: connection.close()
        return content

    def _apiurl(self, path):
        return "/%s%s" % (APIVSN, path)

    #NOTICE: for test
    def poll(self):
        data = {'domain' : self.domain,
                'ticket': self.ticket,
                'callback': 'alert'}
        return self._httpget("/packets", data)


