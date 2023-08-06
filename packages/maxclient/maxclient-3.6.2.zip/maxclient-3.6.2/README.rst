MAXClient
=========

Client library wrapper to access MAX API.

Authentication
---------------

MaxClient uses MAX api's, so a valid max OAuth2 username/token pair is needed to make
any requests. To authenticate a maxlient and leave it ready to use, create a maxclient instance, specifying both Max server url and Oauth2 Server URL: ::

    >>> from maxclient import MaxClient
    >>> client = MaxClient('http://max.server.com', oauth_server='http://oauth.server.com')

Once you have the client instance, you can authenticate it using the username/token pair: ::

    >>> client.setActor('user.name')
    >>> client.setToken('NLfIgUgBgODd4sdAgDsFgdAffFigfBf0')

If you don't have the token for your username, maxclient can grab it for you, providing the password from which the token was generated originally: ::

    >>> client.login(username='user.name', password='password')

``client.login`` becomes interactive if username or password are not provided, so you can use it on cli scripts: ::

    client.login()
    >>> Username: user.name
    >>> Password: *********

Usage
------

There are two versions of the client, one is rpc-like and the other one is rest-ish. The default one (rpc) one implements a method for every api endpoint available on max, for example: ::

    >>> client.addUser('user.name')
    >>> client.getUser('user.name')

rpc-client returns responses with 3 value in a tuple, in the form: ::

    (True, 201, {})

Where the first value is wether the request did finish succesfully, the second the response code of the request, and the third the response content. Response content may be a dict or list loaded from a json, or None if no valid json response found

Note that not all endpoints may be implemented in the rpc-client, as a different method is needed for every endpoint. For parameters of every method, see code in client.py


RESt-ish client
---------------

The rest-ish client is an attempt to make a generic wrapper for max api, so you can easily access all available endpoints with a unique client, and without the need for updating it constantly. The authentication is like in the rpc client, you just have to import it from a different location: ::

    >>> from maxclient.rest import MaxClient

To use this client, you have to know how max apis works and how they are structured, as the access to the api is implemented by mimicking url access, for example. To access the endpoint to add a user, as described on max documentation, you have to make a ``POST`` request to ``/people/{username}``. To make this with maxclient: ::

    >>> maxclient.people['user.name'].post()

Where ``people`` is a resource collection (a fixed name on the endpoint url), and 'user.name' is a resource item (a variable name on the endpoint url). So, resource collections are accessed as attributes, and resource items as dict-like accessors. Both resource items and resource collections can contain each other: ::

    >>> maxclient.people['user.name'].activities.get()

The last part of the command, indicates the method which will be used to access the endpoint. Resource items and collection objects are lazy, so any action will be executed until a method executed on top of a resource.

Named parameters passed to the client will be passed as json when doing ``.post()`` and ``.put()`` requests. So if we execute: ::

    >>> maxclient.people['user.name'].post(displayName='User Name')

a json will be generated from kwargs and sent in the request body: ::

    {
        "displayName": "User Name"
    }

if you want you can prepare a dict with all params that need to be in that json, and pass it through the ``data`` argument, and the result will be the same. if data argument is present, all other kwargs are ignored: ::

    >>> params = dict(displayName='User Name')
    >>> maxclient.people['user.name'].post(data=params)

Some endpoints methods have defined some sensible defaults. You can view the defaults defined in defaults.py, or inspect them by code: ::

    >>> maxclient.people['user.name'].defaults('post')
    {'object': {'objectType': 'note'}}

This defaults are used as a base which is updated using the kwargs provided. I this way, when we make this request: ::

    >>> maxclient.people['user.name'].post(generator='Twitter')

The data that will be send in the request body will be a combination of the defaults and kwargs: ::

    {
        "object": {
            "objectType": "note"
        }
        "generator": "Twitter"
    }

You can pass kwargs in the form key_subkey, and will be interpreted as nested keys. So you can do things like: ::

>>> maxclient.people['user.name'].post(generator='Twitter', object_content='Hello world')

That results in the following request body: ::

    {
        "object": {
            "objectType": "note",
            "content": "Hellow World"
        }
        "generator": "Twitter"
    }

If your requests needs query string parameters, you must feed them trough the ``qs`` argument as a dict, and the key-value pairs will be urlencoded to a querystring, for example, to limit the results of the request with a  ``?limit01``: ::

    >>> maxclient.people['carles.bruguera'].activities.get(qs={'limit': 1})


And the last thing, if you need to upload a file, feed the file object or stream object trough the file_upload param as follows. Feed the raw open file, WITHOUT reading it, we need the object not the content of the file: ::

    >>> avatar = open('/path/to/avatar.png', 'rb')
    >>> maxclient.people['carles.bruguera'].avatar.post(upload_file=avatar)

Maxclient will respond with the parsed json response of max when the request succedded, and will raise an RequestError exception in any other case, which message will indicate the reason of the error.



For more information on max see:

https://github.com/UPCnet/max
https://github.com/UPCnet/maxserver.devel
