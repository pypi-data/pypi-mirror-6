=======
DryDock
=======

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
* Container supervisor utilizing the Docker_ API.

TODO
----

* Provide a better update path.
* Add a stateless shareable mysql container to prepare and specification.
* Better support for stateless-ness and volumes
* Better unittest coverage eg. reports.

.. _Nginx: http://wiki.nginx.org/
.. _YAML: http://wikipedia.org/wiki/YAML
.. _Docker: https://www.docker.io/


Documentation
-------------

The full documentation is at http://dry-dock.readthedocs.org.



History
-------

0.4.3 (12-03-2014)
++++++++++++++++++

* Fix: use ``--name`` for naming containers for future proofing.
* Fix: use ``--dns`` for future proofing.

0.4.2 (11-03-2014)
++++++++++++++++++

* Fix: allow self connections to the host when nginx blocks external.

0.4.1 (09-03-2014)
++++++++++++++++++

* Fix: check for config files before removing them.
* Fix: ``supervise`` command will now recreate the nginx container each run.

0.4.0 (08-03-2014)
++++++++++++++++++


* Added: ``supervise`` command line command. DryDock has its own supervisor!
* Added: ``start`` and ``stop`` command line commands.
* Added: ``data`` in subcontainer specification maps volumes at
``/mnt/drydock``.
* Fix: All containers are passed their FQDN as their hostname
* Fix: ``pull`` command also grabs the containers required for the
``prepare`` command.
* Fix: Pass host timezone to subcontainers.
* Fix: volumes now go map to ``/var/lib/{domain}/{name}/``.

0.3.0 (28-02-2014)
++++++++++++++++++

* Added: reports at the end of running all the major commands.
* Added: ``envs`` to specification for environment variable definitions.
* Added: ``command`` to specification for run command definition.
* Added: ``pull`` command to download all images required for the
specification.
* Added ``specification`` to specification for external specification links.

0.2.0 (25-02-2014)
++++++++++++++++++

* Added: supervisor config writing is now an option.
* Added: deconstruct command to remove a specification.

0.1.0 (25-02-2014)
++++++++++++++++++

* First release on PyPI.


