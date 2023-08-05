
Webim-python
============

Webim python client for nextalk.im


Usage
=====


	import webim 

	user = {'id': 'uid1', 'nick': 'user1', 'presence': 'online', 'show': 'available'}

	c = webim.Client(user, 'localhost', 'public', host='nextalk.im', port = 8000)

	c.online(['uid1','uid2','uid3'], ['grp1','grp2','grp3'])

	c.offline()

API
===

Online
------
    
    buddies = ['uid1', 'uid2', 'uid3']
    
    groups = ['gid1', 'gid2', 'gid3']

    c.online(buddies, groups)

Offline
-------

    c.offline()


Update Presence
---------------

    presence = {
            'type': 'show',
            'show':  'away',
            'status': 'Away' 
    }

    status, resp = self.client.presence(presence)

Send Message
-------------

    message = {
        'to': 'uid2',
        'nick': 'user1',
        'body': 'hahaha',
        'timestamp': time.time()*1000,
        'type': 'chat',
        'style': '' 
    }
    status, resp = self.client.message(message)

Push Message
-------------

    c = Client(self.user, "localhost", "public")

    from = 'uid3'

    message = {
        'to': 'uid2',
        'nick': 'user3',
        'body': 'hahaha',
        'timestamp': time.time()*1000,
        'type': 'chat',
        'style': '' 
    }

    status, resp = c.push(from, message) 

Send Status
-----------

    status = {
        'to': 'uid2',
        'show': 'typeing',
        'status': 'user1 is typing' 
    }
    status, resp = c.status(status)


Retrieve Presences
------------------

    uids = ['uid1', 'uid2']

    status, json = c.presences(uids)


Retrieve group members
----------------------

    gid = 'gid1'

    status, json = c.members(gid)

Join Group
----------

    gid = 'gid1'

    c.join(gid)   


Leave Group
-----------

    gid = 'gid1'

    c.leave(gid)


Author
============

http://nextalk.im

http://github.com/webim

Contact
============

ery.lee at gmail.com

