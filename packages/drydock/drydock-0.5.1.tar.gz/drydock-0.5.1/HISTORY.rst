.. :changelog:

History
-------

0.5.1 (15-03-2014)
++++++++++++++++++

* Added: Customize your network interfaces, ips, and dns from cli.
* Fix: cleaned up template storage to allow manipulation.

0.5.0 (15-03-2014)
++++++++++++++++++

.. warning::
This release has a major emphasis on the ``master`` command and containers
and is released early to facilitate testing.

* Changed: ``master`` command now takes a specification to automatically
build it.
* Removed: any usage of ``supervisord`` in favor of the new
``drydock supervisor``.

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
