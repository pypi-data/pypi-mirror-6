======
YamJam
======
*keeping private data out of source control and applying DRY principles for resource information since 2009*

YamJam is a multi-project, shared, yaml based configuration system. It is also a mechanism to keep secret/private data from leaking out to source control systems (i.e. git, bitbucket, svn, et al) by factoring out sensitive data from your commits.

* Factor out sensitive data from your Django settings.py file
* Makes install by source control by allowing different configs on your dev, staging and production machines
* Don't Repeat Yourself (DRY) Resource configuration

Tested on Python 2.7, 3.2, 3.3, 3.4

.. image:: https://drone.io/bitbucket.org/dundeemt/yamjam/status.png
    :target: https://drone.io/bitbucket.org/dundeemt/yamjam/latest
    :alt: Build Status


------------
Installation
------------
::

  pip install yamjam
  mkdir ~/.yamjam
  touch ~/.yamjam/config.yaml
  chmod -R go-rwx ~/.yamjam


-----------
What Next?
-----------

* **License**: BSD

* **Documentation**: `View Docs <http://yamjam.readthedocs.org/en/latest/>`_

* **Project**: `View Projectt <https://bitbucket.org/dundeemt/yamjam>`_

* **Contributing**: `Do <http://yamjam.readthedocs.org/en/latest/contributing.html>`_

We work so well with Django, you'd think we should spell our name YamDjam