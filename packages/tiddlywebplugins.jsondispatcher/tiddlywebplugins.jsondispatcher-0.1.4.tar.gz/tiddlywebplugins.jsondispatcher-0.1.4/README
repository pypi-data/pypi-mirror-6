# About

A TiddlyWeb plugin to allow the dispatching of tiddlers to non-Python handlers by serialising tiddler data to JSON.

The primary purpose of this plugin is for use with websockets to deliver realtime tiddler updates via [beanstalkd](http://kr.github.io/beanstalkd/).
For more explanation [read this](http://cdent.tiddlyspace.com/TiddlySpaceSockets).

# Requirements

* [Python](http://www.python.org/)
* make
* A working TiddlySpace instance to test against
* [py.test](http://pytest.org/latest/) to run the tests

# Contributing

`setup.py` is used to package up the plugin and install it.

Plugin code lives in the `tiddlywebplugins` directory.

Tests live in the `test` directory.

# Usage

`make test` runs the tests.  Currently there is just the one that 
ensures the plugin can be imported.

`make install` installs the plugin as a package on your system 
(you may need sudo for this.)

## Configuration for TiddlySpace

Edit `tiddlywebconfig.py` to include the following config:

    'use_dispatcher': True,
    'beanstalk_listeners': ['tiddlywebplugins.jsondispatcher']

The plugin is registered as a beanstalk listener as that is where it receives incoming tiddler data from.

For more details on usage run:

    pydoc tiddlywebplugins/jsondispatcher.py

# Credits

@cdent is the original author of `jsondispatcher.py`.  I've just packaged it up a bit.

# See Also

See the [tiddlyspace websockets](https://github.com/TiddlySpace/tiddlyspacesockets) node application that this plugin works with.
