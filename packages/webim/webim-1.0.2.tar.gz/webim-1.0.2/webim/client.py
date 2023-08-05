#!/usr/bin/env python
#coding: utf-8

"""
python webim client

Overview
========

See U{the Webim homepage<http://www.github.com/webim>} for more about webim.

Usage summary
=============

This should give you a feel for how this module operates::

    import webim 
    user = {'uid': 'uid1', 'nick': 'user1', 'presence': 'online', 'show': 'available', 'status': ''}
    c = webim.Client(user, 'domain', 'apikey', host='127.0.0.1', port = 8000)
    c.online(['uid1','uid2','uid3'], ['grp1','grp2','grp3'])
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
import urllib
import urllib2
import hashlib

# ==============================================================================
# Helpers
# ==============================================================================
def encode_utf8(data_dict):
    for key, value in data_dict.iteritems():
        if isinstance(value, unicode):
            data_dict[key] = value.encode('utf8')
    return data_dict

# ==============================================================================
# Client
# ==============================================================================    
class Client:
    
    def __init__(self, user, domain, apikey,
                 ticket=None, host = 'localhost', port=8000, timeout=10):
        """
        Create a new Client object with the given host and port

        @param user: user
        @param host: host
        @param port: port
        """
        self.user = user
        self.domain = domain
        self.apikey = apikey
        self.ticket = ticket
        self.host = host
        self.port = port
        self.timeout = timeout
        
    def online(self, buddies, groups):
        """
        Client online
        """
        reqdata = self._reqdata
        reqdata.update({
            'buddies': ','.join(buddies),
            'groups': ','.join(groups),
            'name': self.user['id'],
            'nick': self.user['nick'],
            'show': self.user['show'],
            'status': self.user['status']
        })
        status, body = self._httpost('/presences/online', reqdata)
        respdata = json.loads(body)
        print 'online.respdata: ', respdata
        if(status == 200): self.ticket = respdata['ticket']
        return (status, respdata)

    def offline(self):
        """
        Client offline
        """
        status, body = self._httpost('/presences/offline', self._reqdata)
        respdata = json.loads(body)
        return (status, respdata)

    def presence(self, presence):
        """
        Send Presence
        """
        reqdata = self._reqdata
        reqdata.update({
            'nick': self.user['nick'],   
            'show': presence['show'],
            'status': presence['status']
        })
        status, body = self._httpost('/presences/show', reqdata)
        return (status, json.loads(body))

    def message(self, message):
        """
        Send Message
        """
        reqdata = self._reqdata
        reqdata.update({
            'nick': self.user['nick'],
            'type': message['type'],
            'to': message['to'],
            'body': message['body'],
            'style': message['style'],
            'timestamp': message['timestamp']
        })
        status, body = self._httpost('/messages', reqdata)
        return (status, json.loads(body))

    #TODO: refactor later
    def push(self, from1, message):
        """
        Push Message
        """
        reqdata = self._reqdata
        reqdata.update({
            'from': from1,
            'nick': self.user['nick'],
            'type': message['type'],
            'to': message['to'],
            'body': message['body'],
            'style': message['style'],
            'timestamp': message['timestamp']
        })
        status, body = self._httpost('/messages', reqdata)
        return (status, json.loads(body))

    def status(self, status):
        """
        Send Status
        """
        reqdata = self._reqdata
        reqdata.update({
            'nick': self.user['nick'],
            'to': status['to'],
            'show': status['show']
        })
        status, body = self._httpost('/statuses', reqdata)
        return (status, json.loads(body))

    def presences(self, ids):
        """
        Read presences
        """
        reqdata = self._reqdata
        reqdata.update({
            'ids': ",".join(ids)
        })
        status, body = self._httpget("/presences", reqdata)
        return (status, json.loads(body))

    def members(self, gid):
        """
        Read group members
        """
        reqdata = self._reqdata
        reqdata.update({
            'group': gid
        })
        status, body = self._httpget('/group/members', reqdata)
        return (status, json.loads(body))
            
    def join(self, gid):
        """
        Join group 
        """
        reqdata = self._reqdata
        reqdata.update({
            'nick': self.user['nick'],
            'group': gid
        })
        status, body = self._httpost('/group/join', reqdata)
        return (status, json.loads(body))
            
    def leave(self, gid):
        """
        Leave group
        """
        reqdata = self._reqdata
        reqdata.update({
            'nick': self.user['nick'],
            'group': gid
        })
        status, body = self._httpost('/group/leave', reqdata)
        return (status, json.loads(body))
        
    @property
    def _reqdata(self):
        data = {
            'version': APIVSN,
            'apikey': self.apikey, 
            'domain': self.domain
        }
        if self.ticket is not None: 
            data['ticket'] = self.ticket
        return data

    def _httpget(self, path, params=None):
        """
        Http Get
        """
        url = self._apiurl(path)
        
        if params is not None:
            print 'GET.url:', url
            print 'GET.params: ', params
            url += "?" + urllib.urlencode(encode_utf8(params))
            try:
                if __debug__: print "GET %s" % url
                resp = urllib2.urlopen(url, timeout=self.timeout)
                body = resp.read()
                if __debug__: print body
                return (resp.getcode(), body)
            except urllib2.HTTPError, e:
                raise e
        
    def _httpost(self, path, data):
        """
        Http Post
        """
        url = self._apiurl(path)
        try:
            if __debug__: print "POST %s" % url
            print 'POST.url:', url
            print 'POST.data:', data
            resp = urllib2.urlopen(url, urllib.urlencode(encode_utf8(data)), self.timeout)
            body = resp.read()
            if __debug__: print body
            return (resp.getcode(), body)
        except urllib2.HTTPError, e:
            raise e

    def _apiurl(self, path):
        return "http://%s:%d/%s%s" % (self.host, self.port, APIVSN, path)

    #NOTICE: for test
    def poll(self):
        data = {'domain' : self.domain,
                'ticket': self.ticket,
                'callback': 'alert'}
        return self._httpget("/packets", data)

