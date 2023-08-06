=============================
DryDock
=============================

.. image:: https://badge.fury.io/py/drydock.png
    :target: http://badge.fury.io/py/drydock
    
.. image:: https://travis-ci.org/Nekroze/drydock.png?branch=master
    :target: https://travis-ci.org/Nekroze/drydock

.. image:: https://pypip.in/d/drydock/badge.png
    :target: https://pypi.python.org/pypi/drydock

A Docker cluster construction utility.

DryDock takes a simple (YAML_) specification file then can construct and
configure a cluster of Docker_ containers. DryDock will automatically
setup a reverse proxy, exposure of ports, and even persistent storage to
allow for easy future upgrading by simply rebuilding the DryDock
specification!

Features
--------

* Simple YAML_ configuration.
* Automatic Docker_ cluster provisioning/configuration
* Nginx_ reverse proxy configuration with HTTPS/SSL support
* Easy setup for persistent volumes.
* Share your DryDock specifications with the world.

TODO
----

* Make a better update path. Remove old containers etc.

.. _Nginx: http://wiki.nginx.org/
.. _YAML: http://wikipedia.org/wiki/YAML
.. _Docker: https://www.docker.io/