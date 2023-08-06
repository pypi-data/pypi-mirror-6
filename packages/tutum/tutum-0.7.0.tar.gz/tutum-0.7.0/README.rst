tutum
=====

CLI for Tutum. Full documentation available at `http://docs.tutum.co/reference/cli/ <http://docs.tutum.co/reference/cli/>`_


Installing the CLI
------------------

In order to install the Tutum CLI, you can use ``pip install``:

.. sourcecode:: bash

    pip install tutum

Now you can start using it:

.. sourcecode:: none

    $ tutum -h
    usage: tutum [-h] [-v] {login,apps,run,inspect,start,stop,terminate,logs,scale,alias,ps,inspect-container,start-container,stop-container,terminate-container,logs-container}
                           ...

    Tutum's CLI

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit

    Tutum's CLI commands:
     {login,apps,run,inspect,start,stop,terminate,logs,scale,alias,ps,inspect-container,start-container,stop-container,terminate-container,logs-container}
       login               Login into Tutum
       apps                List all applications
       run                 Create and run an application
       inspect             Inspect an application
       start               Start an application
       stop                Stop an application
       terminate           Terminate an application
       logs                Get logs from an application
       scale               Scale an application
       alias               Change application's dns
       ps                  List all containers
       inspect-container   Inspect a container
       start-container     Start a container
       stop-container      Stop a container
       terminate-container
                           Terminate a container
       logs-container      Get logs from a container


Authentication
--------------

In other to manage your apps and containers running on Tutum, you need to log into Tutum in any of the following ways
(will be used in this order):

* Login using Tutum CLI or storing it directly in a configuration file in ``~/.tutum``:

.. sourcecode:: bash

    $ tutum login
    Username: admin
    Password:
    Login succeeded!

Your login credentials will be stored in ``~/.tutum``:

.. sourcecode:: ini

    [auth]
    user = "username"
    apikey = "apikey"

* Set the environment variables ``TUTUM_USER`` and ``TUTUM_APIKEY``:

.. sourcecode:: bash

    export TUTUM_USER=username
    export TUTUM_APIKEY=apikey


Quick examples
--------------

Applications
^^^^^^^^^^^^

.. sourcecode:: none

    $ tutum apps
    Name       UUID      State           Image                   Size    Deployed datetime    Web Hostname
    ---------  --------  --------------  ----------------------  ------  -------------------  ----------------------------
    mysql      663f8063  Running         tutum/mysql:latest      XS      2 minutes ago
    wordpress  058df79b  Partly running  tutum/wordpress:latest  XS      1 hour ago           wordpress-admin.dev.tutum.io
    $ tutum inspect 663f8063-1d15-4010-af0c-5ef828de5964
    {'autodestroy': u'OFF',
     'autoreplace': u'OFF',
     'autorestart': u'OFF',
     'container_envvars': [],
     'container_ports': [{u'application': u'/api/v1/application/663f8063-1d15-4010-af0c-5ef828de5964/',
                          u'inner_port': 3306,
                          u'outer_port': None,
                          u'protocol': u'tcp'}],
     'container_size': u'XS',
     'containers': [u'/api/v1/container/94604255-d575-41a2-8e86-886c4d86fca3/',
                    u'/api/v1/container/7693226e-85b6-4cec-a122-e93ab90413e4/'],
     'current_num_containers': 2,
     'deployed_datetime': u'Thu, 3 Apr 2014 19:47:44 +0000',
     'destroyed_datetime': None,
     'entrypoint': u'',
     'image_name': u'tutum/mysql:latest',
     'image_tag': u'/api/v1/image/tutum/mysql/tag/latest/',
     'link_variables': {u'MYSQL_1_PORT': u'tcp://mysql-1-admin.atlas-dev.tutum.io:49309',
                        u'MYSQL_1_PORT_3306_TCP': u'tcp://mysql-1-admin.atlas-dev.tutum.io:49309',
                        u'MYSQL_1_PORT_3306_TCP_ADDR': u'mysql-1-admin.atlas-dev.tutum.io',
                        u'MYSQL_1_PORT_3306_TCP_PORT': u'49309',
                        u'MYSQL_1_PORT_3306_TCP_PROTO': u'tcp',
                        u'MYSQL_3_PORT': u'tcp://mysql-3-admin.atlas-dev.tutum.io:49308',
                        u'MYSQL_3_PORT_3306_TCP': u'tcp://mysql-3-admin.atlas-dev.tutum.io:49308',
                        u'MYSQL_3_PORT_3306_TCP_ADDR': u'mysql-3-admin.atlas-dev.tutum.io',
                        u'MYSQL_3_PORT_3306_TCP_PORT': u'49308',
                        u'MYSQL_3_PORT_3306_TCP_PROTO': u'tcp',
                        u'MYSQL_TUTUM_API_URL': u'https://app-test.tutum.co/api/v1/application/663f8063-1d15-4010-af0c-5ef828de5964/'},
     'linked_from_application': [],
     'linked_to_application': [],
     'name': u'mysql',
     'public_dns': None,
     'resource_uri': u'/api/v1/application/663f8063-1d15-4010-af0c-5ef828de5964/',
     'roles': [],
     'run_command': u'/run.sh',
     'running_num_containers': 2,
     'started_datetime': u'Mon, 7 Apr 2014 23:47:01 +0000',
     'state': u'Running',
     'stopped_datetime': None,
     'stopped_num_containers': 0,
     'target_num_containers': 2,
     'unique_name': u'mysql',
     'uuid': u'663f8063-1d15-4010-af0c-5ef828de5964',
     'web_public_dns': None}
    $ tutum scale 663f8063-1d15-4010-af0c-5ef828de5964 3
    663f8063-1d15-4010-af0c-5ef828de5964
    $ tutum stop 663f8063-1d15-4010-af0c-5ef828de5964
    663f8063-1d15-4010-af0c-5ef828de5964
    $ tutum start 663f8063-1d15-4010-af0c-5ef828de5964
    663f8063-1d15-4010-af0c-5ef828de5964
    $ tutum logs 663f8063-1d15-4010-af0c-5ef828de5964
    ======>mysql-1 <======
    => Creating MySQL admin user with random password
    => Done! [...]
    $ tutum terminate 663f8063-1d15-4010-af0c-5ef828de5964
    663f8063-1d15-4010-af0c-5ef828de5964


Containers
^^^^^^^^^^

.. sourcecode:: none

    $ tutum ps -a -i 058df79b
    Name         UUID      State    Image                   Run Command    Size      Exit Code  Deployed datetime    Ports
    -----------  --------  -------  ----------------------  -------------  ------  -----------  -------------------  --------------------------------------------------------------------------------------------------------
    wordpress-1  d47102dc  Running  tutum/wordpress:latest  /run.sh        XS                0  1 hour ago           wordpress-1-admin.atlas-dev.tutum.io:49213->80/tcp, wordpress-1-admin.atlas-dev.tutum.io:49212->3306/tcp
    wordpress-2  52b84ae9  Stopped  tutum/wordpress:latest  /run.sh        XS                0  41 minutes ago       wordpress-2-admin.atlas-dev.tutum.io:49221->80/tcp, wordpress-2-admin.atlas-dev.tutum.io:49220->3306/tcp
    $ tutum inspect-container d47102dc
    {'application': u'/api/v1/application/64db8436-5d7d-4d02-aa68-78d180c2905e/',
     'autodestroy': u'OFF',
     'autoreplace': u'OFF',
     'autorestart': u'OFF',
     'container_ports': [{u'container': u'/api/v1/container/d47102dc-7bc8-466f-b569-2cb2a6a786e4/',
                          u'inner_port': 80,
                          u'outer_port': 49213,
                          u'protocol': u'tcp'},
                         {u'container': u'/api/v1/container/d47102dc-7bc8-466f-b569-2cb2a6a786e4/',
                          u'inner_port': 3306,
                          u'outer_port': 49212,
                          u'protocol': u'tcp'}],
     'container_size': u'XS',
     'deployed_datetime': u'Mon, 7 Apr 2014 22:32:54 +0000',
     'destroyed_datetime': None,
     'entrypoint': u'',
     'exit_code': 0,
     'exit_code_msg': u'Exit code 0 (Success)',
     'image_name': u'tutum/wordpress:latest',
     'image_tag': u'/api/v1/image/tutum/wordpress/tag/latest/',
     'name': u'wordpress',
     'public_dns': u'wordpress-1-admin.atlas-dev.tutum.io',
     'resource_uri': u'/api/v1/container/d47102dc-7bc8-466f-b569-2cb2a6a786e4/',
     'run_command': u'/run.sh',
     'started_datetime': u'Mon, 7 Apr 2014 23:15:31 +0000',
     'state': u'Running',
     'stopped_datetime': u'Mon, 7 Apr 2014 23:15:14 +0000',
     'unique_name': u'wordpress-1',
     'uuid': u'd47102dc-7bc8-466f-b569-2cb2a6a786e4'}
    $ tutum stop-container d47102dc-7bc8-466f-b569-2cb2a6a786e4
    d47102dc-7bc8-466f-b569-2cb2a6a786e4
    $ tutum start-container wordpress-1
    d47102dc-7bc8-466f-b569-2cb2a6a786e4
    $ tutum logs-container d47102dc-7bc8-466f-b569-2cb2a6a786e4
    => Creating MySQL admin user with random password
    => Done! [...]
    $ tutum terminate-container d47102dc-7bc8-466f-b569-2cb2a6a786e4
    d47102dc-7bc8-466f-b569-2cb2a6a786e4