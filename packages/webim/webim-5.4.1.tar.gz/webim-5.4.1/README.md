
Webim-python
============

WebIM python client for nextalk.im


Usage
=====

    ```python

	import webim 

	endpoint = {'id': 'uid1', 'nick': 'user1', 'presence': 'online', 'show': 'available'}

	c = webim.Client(endpoint, 'domain', 'apikey', host='nextalk.im', port = 8000)

	c.online(['uid1','uid2','uid3'], ['room1','room2','room3'])

	c.offline()


    ```

API
===

Online
------
    
    ```python

    buddies = ['uid1', 'uid2', 'uid3']
    
    rooms = ['room1', 'room2', 'room3']

    c.online(buddies, rooms)

    ```

Offline
-------

    ```python

    c.offline()

    ```


Presence
---------------

    ```python

    show = 'away'

    status = 'Away'

    status, resp = self.client.show(show, status)

    ```

Send Message
-------------

    ```python

    message = {
        'to': 'uid2',
        'nick': 'user1',
        'body': 'hahaha',
        'timestamp': time.time()*1000,
        'type': 'chat',
        'style': '' 
    }
    status, resp = self.client.message(message)

    ```

Push Message
-------------

    ```python

    c = Client(self.endpoint, "localhost", "public")

    message = {
        'from': 'uid3',
        'to': 'uid2',
        'nick': 'user3',
        'body': 'hahaha',
        'timestamp': time.time()*1000,
        'type': 'chat',
        'style': '' 
    }

    status, resp = c.message(message) 

    ```

Send Status
-----------

    ```python

    status = {
        'to': 'uid2',
        'show': 'typeing',
        'status': 'user1 is typing' 
    }
    status, resp = c.status(status)

    ```

Retrieve Presences
------------------

    ```python

    uids = ['uid1', 'uid2']

    status, json = c.presences(uids)

    ```


Retrieve room members
----------------------


    ```python

    room = 'room1'

    status, json = c.members(room)

    ```

Join Room
----------

    ```python

    room = 'room1'

    c.join(room)   

    ```

Leave Room
-----------

    ```python

    room = 'room1'

    c.leave(room)

    ```

Author
============

http://nextalk.im

http://github.com/webim

Contact
============

ery.lee at gmail.com

