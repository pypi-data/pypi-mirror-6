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
                 
                 {login,search,open,apps,ps,run,inspect,start,stop,terminate,logs,scale,alias,build,images,add,remove,update,push}
                 ...
    
    Tutum's CLI
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
    
    Tutum's CLI commands:
      {login,search,open,apps,ps,run,inspect,start,stop,terminate,logs,scale,alias,build,images,add,remove,update,push}
        login               Login into Tutum
        search              Search for images in the Docker Index
        open                Open last web application created in Tutum
        apps                List applications
        ps                  List containers
        run                 Create and run an application
        inspect             Inspect an application or a container
        start               Start an application or a container
        stop                Stop an application or a container
        terminate           Terminate an application or a container
        logs                Get logs from an application or a container
        scale               Scale an application
        alias               Change application's dns (only for applications
                            running in Tutum)
        build               Build an image
        images              List private and local images
        add                 Add a private image
        remove              Remove a private image
        update              Update a private image
        push                Push an image or a repository to Tutum registry



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

    $ tutum ps
    ---- CONTAINERS IN TUTUM ----
    NAME                   UUID      STATUS        IMAGE                                             RUN COMMAND    SIZE      EXIT CODE  DEPLOYED       PORTS
    redis-1                f0225c74  ▶ Running     tutum/redis:latest                                /run.sh        XS                0  2 days ago     redis-1-admin.atlas-dev.tutum.io:50303->6379/tcp
    redis-2                5ee84d78  ▶ Running     tutum/redis:latest                                /run.sh        XS                0  2 days ago     redis-2-admin.atlas-dev.tutum.io:49153->6379/tcp
    redis-3                fc17d7fd  ▶ Running     tutum/redis:latest                                /run.sh        XS                0  2 days ago     redis-3-admin.atlas-dev.tutum.io:49154->6379/tcp
    ubuntu-precise-1       6e36d45e  ▶ Running     tutum/ubuntu-precise:latest                       /run.sh        XS                   2 days ago     ubuntu-precise-1-admin.atlas-dev.tutum.io:49160->22/tcp
    db-1                   9d4ef371  ▶ Running     tutum/mysql:latest                                /run.sh        XS                   1 day ago      db-1-admin.atlas-dev.tutum.io:49155->3306/tcp
    ubuntu-precise-2       09b62491  ◼ Stopped     tutum/ubuntu-precise:latest                       printenv       XS                0  1 day ago      22/tcp
    wordpress-stackable-1  73bb355c  ◼ Stopped     r-test.tutum.co/admin/wordpress-stackable:latest  /run.sh        XS              255  1 day ago      wordpress-stackable-1-admin.atlas-dev.tutum.io:49157->80/tcp
    mysql-1                e7986e00  ✘ Terminated  tutum/mysql:latest                                /run.sh        XS                0  6 hours ago    mysql-1-admin.atlas-dev.tutum.io:49159->3306/tcp
    mysql-1                e36d126a  ▶ Running     tutum/mysql:latest                                /run.sh        XS                0  3 minutes ago  mysql-1-admin.atlas-dev.tutum.io:49164->3306/tcp
    mysql-2                a0aca820  ▶ Running     tutum/mysql:latest                                /run.sh        XS                0  3 minutes ago  mysql-2-admin.atlas-dev.tutum.io:49165->3306/tcp
    mysql-3                3b532175  ▶ Running     tutum/mysql:latest                                /run.sh        XS                0  3 minutes ago  mysql-3-admin.atlas-dev.tutum.io:49166->3306/tcp
    mysql-4                faba26e8  ▶ Running     tutum/mysql:latest                                /run.sh        XS                0  3 minutes ago  mysql-4-admin.atlas-dev.tutum.io:49167->3306/tcp
    
    ---- LOCAL CONTAINERS ----
    NAME    UUID    STATUS    IMAGE    RUN COMMAND    SIZE    EXIT CODE    DEPLOYED    PORTS

    $ tutum inspect 9d4ef371
    {
      "unique_name": "db-1", 
      "public_dns": "db-1-admin.atlas-dev.tutum.io", 
      "deployed_datetime": "Thu, 24 Apr 2014 21:32:59 +0000", 
      "autorestart": "OFF", 
      "uuid": "9d4ef371-abbd-4372-8b15-ab9c484ca4cb", 
      "destroyed_datetime": null, 
      "exit_code": null, 
      "linked_to_application": [], 
      "autoreplace": "OFF", 
      "application": "/api/v1/application/a64907f6-cf30-47da-92f1-aaabdb62fbc7/", 
      "state": "Running", 
      "entrypoint": "", 
      "run_command": "/run.sh", 
      "container_ports": [
        {
          "inner_port": 3306, 
          "protocol": "tcp", 
          "container": "/api/v1/container/9d4ef371-abbd-4372-8b15-ab9c484ca4cb/", 
          "outer_port": 49155
        }
      ], 
      "link_variables": {
        "DB_1_PORT_3306_TCP_ADDR": "db-1-admin.atlas-dev.tutum.io", 
        "DB_1_PORT": "tcp://db-1-admin.atlas-dev.tutum.io:49155", 
        "DB_1_PORT_3306_TCP_PROTO": "tcp", 
        "DB_1_PORT_3306_TCP_PORT": "49155", 
        "DB_1_PORT_3306_TCP": "tcp://db-1-admin.atlas-dev.tutum.io:49155"
      }, 
      "linked_from_application": [], 
      "image_name": "tutum/mysql:latest", 
      "started_datetime": "Thu, 24 Apr 2014 21:32:59 +0000", 
      "stopped_datetime": null, 
      "name": "db", 
      "roles": [], 
      "exit_code_msg": null, 
      "container_envvars": [
        {
          "container": "/api/v1/container/9d4ef371-abbd-4372-8b15-ab9c484ca4cb/", 
          "value": "test", 
          "key": "MYSQL_PASS"
        }
      ], 
      "autodestroy": "OFF", 
      "image_tag": "/api/v1/image/tutum/mysql/tag/latest/", 
      "container_size": "XS", 
      "resource_uri": "/api/v1/container/9d4ef371-abbd-4372-8b15-ab9c484ca4cb/"
    }
    
    $ tutum stop 9d4ef371
    9d4ef371-abbd-4372-8b15-ab9c484ca4cb
    
    $ tutum start 9d4ef371
    9d4ef371-abbd-4372-8b15-ab9c484ca4cb
    
    $ tutum logs 9d4ef371
    => Creating MySQL admin user with preset password
    => Done![...]
    
    $ tutum terminate 9d4ef371
    9d4ef371-abbd-4372-8b15-ab9c484ca4cb
