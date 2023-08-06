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
     {login,apps,create,inspect,start,stop,terminate,logs,scale,alias,ps,inspect-container,start-container,stop-container,terminate-container,logs-container}
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
        Name       UUID      State           Image                                      Size    Deployed datetime               Web Hostname
    ---------  --------  --------------  -----------------------------------------  ------  ------------------------------  ------------------------------
    mysql      663f8063  Running         /api/v1/image/tutum/mysql/tag/latest/      XS      Thu, 3 Apr 2014 19:47:44 +0000
    wordpress  058df79b  Partly running  /api/v1/image/tutum/wordpress/tag/latest/  M       Thu, 3 Apr 2014 20:24:36 +0000  wordpress-3-admin.dev.tutum.io
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
     'started_datetime': u'Fri, 4 Apr 2014 00:08:22 +0000',
     'state': u'Running',
     'stopped_datetime': u'Thu, 3 Apr 2014 23:37:59 +0000',
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

    $ tutum ps
    Name       UUID      State         Image                                      Run Command    Size      Exit Code  Deployed datetime               Ports
    ---------  --------  ------------  -----------------------------------------  -------------  ------  -----------  ------------------------------  --------------------------------------------------------------------------------------------------------
    wordpress  a7765c40  Running       /api/v1/image/tutum/wordpress/tag/latest/  /run.sh        M                    Thu, 3 Apr 2014 20:24:34 +0000  wordpress-1-admin.atlas-dev.tutum.io:49306->80/tcp, wordpress-1-admin.atlas-dev.tutum.io:49305->3306/tcp
    wordpress  40a11d2b  Running       /api/v1/image/tutum/wordpress/tag/latest/  /run.sh        M                    Fri, 4 Apr 2014 19:36:22 +0000  wordpress-2-admin.atlas-dev.tutum.io:49325->80/tcp, wordpress-2-admin.atlas-dev.tutum.io:49324->3306/tcp
    $ tutum inspect-container a7765c40-32df-433b-8d17-5f9106fd148b
    {'application': u'/api/v1/application/058df79b-6248-476b-890b-c15562f6ef25/',
     'autodestroy': u'OFF',
     'autoreplace': u'OFF',
     'autorestart': u'OFF',
     'container_envvars': [],
     'container_ports': [{u'container': u'/api/v1/container/a7765c40-32df-433b-8d17-5f9106fd148b/',
                          u'inner_port': 80,
                          u'outer_port': 49306,
                          u'protocol': u'tcp'},
                         {u'container': u'/api/v1/container/a7765c40-32df-433b-8d17-5f9106fd148b/',
                          u'inner_port': 3306,
                          u'outer_port': 49305,
                          u'protocol': u'tcp'}],
     'container_size': u'M',
     'deployed_datetime': u'Thu, 3 Apr 2014 20:24:34 +0000',
     'destroyed_datetime': None,
     'entrypoint': u'',
     'exit_code': None,
     'exit_code_msg': None,
     'image_tag': u'/api/v1/image/tutum/wordpress/tag/latest/',
     'link_variables': {u'WORDPRESS_1_PORT_3306_TCP': u'tcp://wordpress-1-admin.atlas-dev.tutum.io:49305',
                        u'WORDPRESS_1_PORT_3306_TCP_ADDR': u'wordpress-1-admin.atlas-dev.tutum.io',
                        u'WORDPRESS_1_PORT_3306_TCP_PORT': u'49305',
                        u'WORDPRESS_1_PORT_3306_TCP_PROTO': u'tcp',
                        u'WORDPRESS_1_PORT_80_TCP': u'tcp://wordpress-1-admin.atlas-dev.tutum.io:49306',
                        u'WORDPRESS_1_PORT_80_TCP_ADDR': u'wordpress-1-admin.atlas-dev.tutum.io',
                        u'WORDPRESS_1_PORT_80_TCP_PORT': u'49306',
                        u'WORDPRESS_1_PORT_80_TCP_PROTO': u'tcp'},
     'linked_from_application': [],
     'linked_to_application': [],
     'name': u'wordpress',
     'public_dns': u'wordpress-1-admin.atlas-dev.tutum.io',
     'resource_uri': u'/api/v1/container/a7765c40-32df-433b-8d17-5f9106fd148b/',
     'roles': [],
     'run_command': u'/run.sh',
     'started_datetime': u'Thu, 3 Apr 2014 20:24:34 +0000',
     'state': u'Running',
     'stopped_datetime': None,
     'unique_name': u'wordpress-1',
     'uuid': u'a7765c40-32df-433b-8d17-5f9106fd148b',
     'web_public_dns': u'wordpress-1-admin.atlas-dev.tutum.io'}
    $ tutum stop-container a7765c40-32df-433b-8d17-5f9106fd148b
    a7765c40-32df-433b-8d17-5f9106fd148b
    $ tutum start-container a7765c40-32df-433b-8d17-5f9106fd148b
    a7765c40-32df-433b-8d17-5f9106fd148b
    $ tutum logs-container a7765c40-32df-433b-8d17-5f9106fd148b
    => Creating MySQL admin user with random password
    => Done! [...]
    $ tutum terminate-container a7765c40-32df-433b-8d17-5f9106fd148b
    a7765c40-32df-433b-8d17-5f9106fd148b
