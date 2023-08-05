===============================
fwissr
===============================

.. image:: https://badge.fury.io/py/fwissr-python.png
    :target: http://badge.fury.io/py/fwissr-python
    
.. image:: https://travis-ci.org/fotonauts/fwissr-python.png?branch=master
        :target: https://travis-ci.org/fotonauts/fwissr-python

.. image:: https://pypip.in/d/fwissr-python/badge.png
        :target: https://crate.io/packages/fwissr-python?version=latest


fwissr-python is a registry configuration tool, compatible with fwissr, its ruby counterpart. Made by fotonauts.

* Free software: MIT license
* Documentation: http://fwissr-python.rtfd.org.

Install
=======


``$ [sudo] pip install fwissr``

Usage
=====

Create the main ``fwissr.json`` configuration file in either ``/etc/fwissr/`` or ``~/.fwissr/`` directory::

   {
     "foo" : "bar",
     "horn" : { "loud" : true, "sounds": [ "TUuuUuuuu", "tiiiiiiIIiii" ] }
   }

In your application, you can access ``fwissr``'s global registry that way::


    from fwissr.fwissr import Fwissr
    Fwissr['/foo']
    # u'bar'
    Fwissr['/horn']
    # {u'sounds': [u'TUuuUuuuu', u'tiiiiiiIIiii'], u'loud': True}
    Fwissr['/horn/loud']
    # True
    Fwissr['/horn/sounds']
    # [u'TUuuUuuuu', u'tiiiiiiIIiii']


In bash you can call the `fwissr` tool::

    $ fwissr /foo
    bar

    # json output
    $ fwissr -j /horn
    {"loud": true, "sounds": ["TUuuUuuuu", "tiiiiiiIIiii"]}

    # pretty print json output
    $ fwissr -j -p /horn
    {
        "loud": true,
        "sounds": [
            "TUuuUuuuu",
            "tiiiiiiIIiii"
        ]
    }

    # dump all registry with pretty print json output
    # NOTE: yes, that's the same as 'fwissr -jp /'
    $ fwissr --dump -jp
    {
      "horn": {
        "loud": true,
        "sound": [
          "TUuuUuuuu",
          "tiiiiiiIIiii"
        ]
      }
    }



Additional configuration file
=============================

Provide additional configuration files with the ``fwissr_sources`` setting in ``fwissr.json``::


    {
      "fwissr_sources": [
        { "filepath": "/etc/my_app.json" }
      ]
    }


The settings for that configuration will be prefixed with the file name.

For example, with that ``/etc/my_app.json``::

    { "foo": "bar", "bar": "baz" }

the settings can be accessed that way::

    from fwissr.fwissr import Fwissr
    
    Fwissr['/my_app']
    #=> { "foo": "bar", "bar": "baz" }
    
    Fwissr['/my_app/foo']
    #=> "bar"

    Fwissr['/my_app/bar']
    #=> "baz"

You can bypass that behaviour with the ``top_level`` setting::

    {
      "fwissr_sources": [
        { "filepath": "/etc/my_app.json", "top_level": true }
      ]
    }


With the ``top_level`` setting activated the configuration settings are added to registry root::

    from fwissr.fwissr import Fwissr

    Fwissr['/']
    #=> { "foo": "bar", "bar": "baz" }

    Fwissr['/foo']
    #=> "bar"

    Fwissr['/bar']
    #=> "baz"


Note that you can provide ``.json`` and ``.yaml`` configuration files.


Directory of configuration files
================================

If the ``filepath`` setting is a directory, then all ``.json`` and ``.yaml`` files in that directory (but NOT in subdirectories) will be imported in the global registry::

    {
      "fwissr_sources": [
        { "filepath": "/mnt/my_app/conf/" },
      ],
    }


With ``/mnt/my_app/conf/database.yaml``::

    production:
      adapter: mysql2
      encoding: utf8
      database: my_app_db
      username: my_app_user
      password: my_app_pass
      host: db.my_app.com


and ``/mnt/my_app/conf/credentials.json``::

    { "key": "i5qw64816c", "code": "448e4wef161" }


the settings can be accessed that way::

    from fwissr.fwissr import Fwissr

    Fwissr['/database']
    #=> { "production": { "adapter": "mysql2", "encoding": "utf8", "database": "my_app_db", "username": "my_app_user", "password": "my_app_pass", "host": "db.my_app.com" } }

    Fwissr['/database/production/host']
    #=> "db.my_app.com"

    Fwissr['/credentials']
    #=> { "key": "i5qw64816c", "code": "448e4wef161" }

    Fwissr['/credentials/key']
    #=> "i5qw64816c"


File name mapping to setting path
=================================

Use dots in file name to define a path for configuration settings.

For example::

    {
      "fwissr_sources": [
        { "filepath": "/etc/my_app.database.slave.json" }
      ]
    }

with that ``/etc/my_app.database.slave.json``::


    { "host": "db.my_app.com", "port": "1337" }

The settings can be accessed that way::

    from fwissr.fwissr import Fwissr

    Fwissr['/my_app/database/slave/host']
    #=> "db.my_app.com"

    Fwissr['/my_app/database/slave/port']
    #=> "1337"


Mongodb source
==============

You can define a mongob collection as a configuration source::

    {
      "fwissr_sources": [
        { "mongodb": "mongodb://db1.example.net/my_app", "collection": "config" }
      ]
    }


Each document in the collection is a setting for that configuration.

The ``_id`` document field is the setting key, and the ``value`` document field is the setting value.

For example::

    > db["my_app.stuff"].find()
    { "_id" : "foo", "value" : "bar" }
    { "_id" : "database", "value" : { "host": "db.my_app.com", "port": "1337" } }

::

    from fwissr.fwissr import Fwissr

    Fwissr['/my_app/stuff/foo']
    #=> "bar"

    Fwissr['/my_app/stuff/database']
    #=> { "host": "db.my_app.com", "port": "1337" }

    Fwissr['/my_app/stuff/database/port']
    #=> "1337"

As with configuration files you can use dots in collection name to define a path for configuration settings. The ``top_level`` setting is also supported to bypass that behaviour. Note too that the ``fwissr`` collection is by default a ``top_level`` configuration (as the ``/etc/fwissr/fwissr.json`` configuration file).


Refreshing registry
===================

Enable registry auto-update with the `refresh` source setting.

For example::

    {
      "fwissr_sources": [
        { "filepath": "/etc/my_app/my_app.json" },
        { "filepath": "/etc/my_app/stuff.json", "refresh": true },
        { "mongodb": "mongodb://db1.example.net/my_app", "collection": "production" },
        { "mongodb": "mongodb://db1.example.net/my_app", "collection": "config", "refresh": true }
      ]
    }

The ``/etc/my_app/my_app.json`` configuration file and the ``production`` mongodb collection are read only once, whereas the settings holded by the ``/etc/my_app/stuff.json`` configuration file and the ``config`` mongodb collection are expired periodically and re-fetched.

The default freshness is 30 seconds, but you can change it with the ``fwissr_refresh_period`` setting::

    {
      "fwissr_sources": [
        { "filepath": "/etc/my_app/my_app.json" },
        { "filepath": "/etc/my_app/stuff.json", "refresh": true },
        { "mongodb": "mongodb://db1.example.net/my_app", "collection": "production" },
        { "mongodb": "mongodb://db1.example.net/my_app", "collection": "config", "refresh": true }
       ],
      "fwissr_refresh_period": 60
    }

The refresh is done periodically in a thread::

    from fwissr.fwissr import Fwissr
    import time

    Fwissr['/stuff/foo']
    #=> "bar"

    # > Change '/etc/my_app/stuff.json' file by setting: {"foo":"baz"}

    # Wait 2 minutes
    time.sleep(120)

    # The new value is now in the registry
    Fwissr['/stuff/foo']
    #=> "baz"


Create a custom registry
========================

``fwissr`` is intended to be easy to setup: just create a configuration file and that configuration is accessible via the global registry. But if you need to, you can create your own custom registry::

    from fwissr.fwissr import Fwissr
    from fwissr.registry import Registry
    from fwissr.source.source import Source
    # create a custom registry
    registry = Registry(refresh_period=20)

    # add configuration sources to registry
    registry.add_source(Source.from_settings({ 'filepath': '/etc/my_app/my_app.json' }))
    registry.add_source(Source.from_settings({ 'filepath': '/etc/my_app/stuff.json', 'refresh': true }))
    registry.add_source(Source.from_settings({ 'mongodb': 'mongodb://db1.example.net/my_app', 'collection': 'production' }))
    registry.add_source(Source.from_settings({ 'mongodb': 'mongodb://db1.example.net/my_app', 'collection': 'config', 'refresh': True }))

    registry['/stuff/foo']
    #=> 'bar'

Create a custom source
======================

Currently ``fwissr.source.file.File`` and ``fwissr.source.mongodb.Mongodb`` are the two kinds of possible registry sources, but you can define your own source:


TODO


Credits
=======

The Fotonauts team: http://www.fotopedia.com

Copyright (c) 2013 Fotonauts released under the MIT license.