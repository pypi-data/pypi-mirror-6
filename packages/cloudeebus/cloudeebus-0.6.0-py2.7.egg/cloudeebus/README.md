
Cloudeebus
==========

Cloudeebus - DBus for the Cloud - is a component which enables calling DBus
 methods and registering on DBus signals from Javascript.


Install
-------

### Installing Cloudeebus from the project root directory:

Cloudeebus will install itself in Python's dist-packages folder. The
 cloudeebus.py wrapper shell goes in the executables path.

	sudo python setup.py install

See the [Getting Started](https://github.com/01org/cloudeebus/wiki/Getting-started)
 section of the [Cloudeebus wiki](https://github.com/01org/cloudeebus/wiki)
 for a list of dependencies to install.


### Running Cloudeebus:

The Cloudeebus server must be run either with credentials and a whitelist to
 restrict access to DBus services, or in opendoor mode.

	usage: cloudeebus.py [-h] [-v] [-d] [-o] [-p PORT] [-c CREDENTIALS]
		             [-w WHITELIST] [-s SERVICELIST] [-n NETMASK]

	Javascript DBus bridge.

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         print version and exit
	  -d, --debug           log debug info on standard output
	  -o, --opendoor        allow anonymous access to all services
	  -p PORT, --port PORT  port number
	  -c CREDENTIALS, --credentials CREDENTIALS
		                path to credentials file
	  -w WHITELIST, --whitelist WHITELIST
		                path to whitelist file (DBus services to use)
	  -s SERVICELIST, --servicelist SERVICELIST
		                path to servicelist file (DBus services to export)
	  -n NETMASK, --netmask NETMASK
		                netmask,IP filter (comma separated.) eg. : -n
		                127.0.0.1,192.168.2.0/24,10.12.16.0/255.255.255.0


Documentation
-------------

  * [Cloudeebus](http://01.org/cloudeebus) project home page on [01.org](http://01.org)
  * [Javascript API](https://github.com/01org/cloudeebus/wiki/API) reference.
  * [Architecture](https://github.com/01org/cloudeebus/wiki/Architecture) block diagram.


Examples
--------

### dbus-tools

The /doc/dbus-tools folder contains dbus-send and dbus-register test pages.
Cloudeebus runs in opendoor mode, the dbus-tools pages have no manifest.

	cloudeebus.py --debug --opendoor --port=9001 &
	firefox ./doc/dbus-tools/dbus-register.html ./doc/dbus-tools/dbus-send.html &

### sample

The /doc/sample folder contains a working sample using credentials, whitelist and manifest.
Cloudeebus runs with credentials and a whitelist that are matched by the
 sample page manifest.

	cloudeebus.py --debug --credentials=./doc/sample/CREDENTIALS --whitelist=./doc/sample/WHITELIST &
	firefox ./doc/sample/cloudeebus.html &

The sample page is also online as a [live demo](http://01org.github.com/cloudeebus/).

### agent

The /doc/agent folder contains a working client sample using credentials, whitelist and manifest and
a working service sample using credentials, servicelist and manifest.
One instance of cloudeebus runs with credentials and a whitelist that are matched by the 
client page manifest.

	cloudeebus.py --debug --credentials=./doc/agent/CREDENTIALS --whitelist=./doc/agent/SAMPLELIST -p 9002 &
	firefox ./doc/agent/client.html &

The other instance of cloudeebus runs with credentials and a servicelist that are matched by the 
server page manifest.

	cloudeebus.py --debug --credentials=./doc/agent/CREDENTIALS --servicelist=./doc/agent/SAMPLELIST -p 9003 &
	firefox ./doc/agent/server.html &


Acknowledgements
----------------

Cloudeebus uses code from the following open-source projects:

  * [AutobahnJS](http://autobahn.ws/js) ([MIT](http://opensource.org/licenses/MIT) License)
  * [AutobahnPython](http://autobahn.ws/python) ([Apache 2.0](http://opensource.org/licenses/Apache-2.0) License)
