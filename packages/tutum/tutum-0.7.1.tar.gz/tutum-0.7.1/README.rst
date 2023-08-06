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
    usage: tutum [-h] [-v]

                 {login,apps,run,inspect,start,stop,terminate,logs,scale,alias,ps,inspect-container,start-container,stop-container,terminate-container,logs-container,images,add,remove,update}
                 ...

    Tutum's CLI

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit

    Tutum's CLI commands:
      {login,apps,run,inspect,start,stop,terminate,logs,scale,alias,ps,inspect-container,start-container,stop-container,terminate-container,logs-container,images,add,remove,update}
        login               Login into Tutum
        apps                List running applications
        run                 Create and run an application
        inspect             Inspect an application
        start               Start an application
        stop                Stop an application
        terminate           Terminate an application
        logs                Get logs from an application
        scale               Scale an application
        alias               Change application's dns
        ps                  List running containers
        inspect-container   Inspect a container
        start-container     Start a container
        stop-container      Stop a container
        terminate-container
                            Terminate a container
        logs-container      Get logs from a container
        images              List private images
        add                 Add a private image
        remove              Remove a private image
        update              Update a private image


Docker image
^^^^^^^^^^^^

You can also install the CLI via Docker:

.. sourcecode:: bash

    docker run tutum/cli -h

You will have to pass your username and API key as environment variables, as the credentials stored via ``tutum login``
will not persist by default:

.. sourcecode:: bash

    docker run -e TUTUM_USER=username -e TUTUM_APIKEY=apikey tutum/cli apps

To make things easier, you might want to use an ``alias`` for it:

.. sourcecode:: bash

    alias tutum="docker run -e TUTUM_USER=username -e TUTUM_APIKEY=apikey tutum/cli"
    tutum apps


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
    Name            UUID      State             Image                        Size    Deployed datetime    Web Hostname
    --------------  --------  ----------------  ---------------------------  ------  -------------------  ----------------------------
    mysql           695061b6  ▶ Running         tutum/mysql:latest           XS      21 hours ago
    ubuntu-precise  d9bcffe8  ▶ Running         tutum/ubuntu-precise:latest  XS      11 hours ago
    wordpress       64db8436  ▶ Partly running  tutum/wordpress:latest       XS      22 hours ago         wordpress-admin.dev.tutum.io
    $ tutum inspect 695061b6
    {'autodestroy': u'OFF',
     'autoreplace': u'OFF',
     'autorestart': u'OFF',
     'container_ports': [{u'application': u'/api/v1/application/695061b6-3a55-4f27-a4f3-ea96221474bd/',
                          u'inner_port': 3306,
                          u'outer_port': None,
                          u'protocol': u'tcp'}],
     'container_size': u'XS',
     'current_num_containers': 1,
     'deployed_datetime': u'Mon, 7 Apr 2014 23:47:01 +0000',
     'destroyed_datetime': None,
     'entrypoint': u'',
     'image_name': u'tutum/mysql:latest',
     'image_tag': u'/api/v1/image/tutum/mysql/tag/latest/',
     'name': u'mysql',
     'public_dns': None,
     'resource_uri': u'/api/v1/application/695061b6-3a55-4f27-a4f3-ea96221474bd/',
     'run_command': u'/run.sh',
     'running_num_containers': 1,
     'started_datetime': u'Mon, 7 Apr 2014 23:47:01 +0000',
     'state': u'Running',
     'stopped_datetime': None,
     'stopped_num_containers': 0,
     'target_num_containers': 1,
     'unique_name': u'mysql',
     'uuid': u'695061b6-3a55-4f27-a4f3-ea96221474bd',
     'web_public_dns': None}
    $ tutum scale 695061b6-3a55-4f27-a4f3-ea96221474bd 3
    695061b6-3a55-4f27-a4f3-ea96221474bd
    $ tutum stop 695061b6-3a55-4f27-a4f3-ea96221474bd
    695061b6-3a55-4f27-a4f3-ea96221474bd
    $ tutum start 695061b6-3a55-4f27-a4f3-ea96221474bd
    695061b6-3a55-4f27-a4f3-ea96221474bd
    $ tutum logs 695061b6-3a55-4f27-a4f3-ea96221474bd
    ======>mysql-1 <======
    => Creating MySQL admin user with random password
    => Done! [...]
    $ tutum terminate 695061b6-3a55-4f27-a4f3-ea96221474bd
    695061b6-3a55-4f27-a4f3-ea96221474bd


Containers
^^^^^^^^^^

.. sourcecode:: none

    $ tutum ps -a -i 695061b6-3a55-4f27-a4f3-ea96221474bd
    Name     UUID      State      Image               Run Command    Size      Exit Code  Deployed datetime    Ports
    -------  --------  ---------  ------------------  -------------  ------  -----------  -------------------  ------------------------------------------------
    mysql-1  6a309404  ▶ Running  tutum/mysql:latest  /run.sh        XS                   21 hours ago         mysql-1-admin.atlas-dev.tutum.io:49222->3306/tcp
    mysql-2  02795686  ▶ Running  tutum/mysql:latest  /run.sh        XS                   40 seconds ago       mysql-2-admin.atlas-dev.tutum.io:49226->3306/tcp
    mysql-3  30a464f8  ▶ Running  tutum/mysql:latest  /run.sh        XS                0  35 seconds ago       mysql-3-admin.atlas-dev.tutum.io:49227->3306/tcp
    $ tutum inspect-container 6a309404
    {'application': u'/api/v1/application/695061b6-3a55-4f27-a4f3-ea96221474bd/',
     'autodestroy': u'OFF',
     'autoreplace': u'OFF',
     'autorestart': u'OFF',
     'container_ports': [{u'container': u'/api/v1/container/6a309404-5d80-4392-bf7e-6757f7f08301/',
                          u'inner_port': 3306,
                          u'outer_port': 49222,
                          u'protocol': u'tcp'}],
     'container_size': u'XS',
     'deployed_datetime': u'Mon, 7 Apr 2014 23:46:59 +0000',
     'destroyed_datetime': None,
     'entrypoint': u'',
     'exit_code': None,
     'exit_code_msg': None,
     'image_name': u'tutum/mysql:latest',
     'image_tag': u'/api/v1/image/tutum/mysql/tag/latest/',
     'name': u'mysql',
     'public_dns': u'mysql-1-admin.atlas-dev.tutum.io',
     'resource_uri': u'/api/v1/container/6a309404-5d80-4392-bf7e-6757f7f08301/',
     'run_command': u'/run.sh',
     'started_datetime': u'Mon, 7 Apr 2014 23:46:59 +0000',
     'state': u'Running',
     'stopped_datetime': None,
     'unique_name': u'mysql-1',
     'uuid': u'6a309404-5d80-4392-bf7e-6757f7f08301'}
    $ tutum stop-container 6a309404-5d80-4392-bf7e-6757f7f08301
    6a309404-5d80-4392-bf7e-6757f7f08301
    $ tutum start-container mysql-1
    6a309404-5d80-4392-bf7e-6757f7f08301
    $ tutum logs-container 6a309404-5d80-4392-bf7e-6757f7f08301
    => Creating MySQL admin user with random password
    => Done! [...]
    $ tutum terminate-container 6a309404-5d80-4392-bf7e-6757f7f08301
    6a309404-5d80-4392-bf7e-6757f7f08301