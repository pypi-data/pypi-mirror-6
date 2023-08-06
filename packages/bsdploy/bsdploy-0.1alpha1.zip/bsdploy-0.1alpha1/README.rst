BSDploy is a tool to deploy `FreeBSD <http://www.freebsd.org>`_ `jails <http://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/jails-intro.html>`_.

Not wanting to re-invent the wheel, under the hood it uses `mr.awsome <https://pypi.python.org/pypi/mr.awsome>`_ for provisioning, `ansible <http://ansible.cc>`_ for configuration and `fabric <http://fabfile.org>`_ for maintenance.


Features
========

 - configure multiple hosts and jails in one canonical ini-file
 - bootstrap complete jail hosts from scratch - both virtual machines, as well as physical ones. ``bsdploy`` will take care of installing FreeBSD for you, including configuration of `ZFS pools <https://wiki.freebsd.org/ZFS>`_ and even encrypts them by default(!) using `GELI <http://www.freebsd.org/doc/handbook/disks-encrypting.html>`_.
 - create new jails simply by adding two or more lines to your configuration file and running ``ploy start`` – bsdploy will take care of configuring the required IP address on the host
 - **ansible support** – no more mucking about with host files: all hosts and their variables defined in ``ploy.conf`` are automatically exposed to ansible. Run them with ``ploy playbook path/to/playbook.yml``.
 - ditto for **Fabric** – run fabric scripts with ``ploy do JAILNAME TASKNAME`` and have all your hosts and their variables at your disposal in ``fab.env``.
 - jails receive private IP addresses by default, so they are not reachable from the outside - for configuration access (i.e. applying ansible playbooks to them or running fabric scripts inside of them) bsdploy transparently configures SSH ProxyCommand based access.
 - Easily configure ``ipnat`` on the jail host to white-list access from the outside – this greatly reduces (sadly not eliminates) the chance of accidentally exposing services to the outside world that shouldn't be.

With bsdploy you can create and configure one or more jail hosts with one or more jails inside them, all configured in one canonical ``ini`` style configuration file (by default in ``etc/ploy.conf)``::

    [ez-master:vm-master]
    host = 127.0.0.1
    port = 47022

    [ez-instance:webserver]
    ip = 10.0.0.2
    fqdn = test.local
    fabfile = deployment/webserver.py

    [ez-instance:database]
    ip = 10.0.0.3
    dbname = production

    [ez-instance:application]
    ip = 10.0.0.4
    version = 1.2.3


Examples
========

To give it a spin, best `check out the example repository <https://github.com/tomster/ezjail-test-vm>`_.

TODO
====

 - documentation *cough*
 - make rc.conf a template (to support non-DHCP jailhost scenario)
 - allow for offline installation of ezjail
 - allow for offline installation of pkgng
 - include poudriere support
 - eliminate need for proxycommand, proxyhost and hooks entries for jail configuration in ploy.conf
 - make the private network for the jails configurable (the hard coded 10.0.0.x is not always desirable)