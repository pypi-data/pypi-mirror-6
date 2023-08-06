import getpass
import ConfigParser
import json
from os.path import join, expanduser

from tutum.api import auth
from tutum.api import exceptions
import tutum

from tutumcli import utils


TUTUM_FILE = '.tutum'
AUTH_SECTION = 'auth'
USER_OPTION = "user"
APIKEY_OPTION = 'apikey'


def authenticate():

    username = raw_input("Username: ")
    password = getpass.getpass()
    try:
        api_key = auth.get_apikey(username, password)
        if api_key is not None:
            config = ConfigParser.ConfigParser()
            config.add_section(AUTH_SECTION)
            config.set(AUTH_SECTION, USER_OPTION, username)
            config.set(AUTH_SECTION, APIKEY_OPTION, api_key)
            with open(join(expanduser('~'), TUTUM_FILE), 'w') as cfgfile:
                config.write(cfgfile)
            print "Login succeeded!"
    except exceptions.TutumAuthError:
        print "Wrong username and/or password. Please try to login again"
    except Exception as e:
        print e


def apps(quiet=False, status=None):
    try:
        app_list = tutum.Application.list(state=status)
        headers = ["NAME", "UUID", "STATUS", "IMAGE", "SIZE (#)", "DEPLOYED", "WEB HOSTNAME"]
        data_list = []
        long_uuid_list = []
        if len(app_list) != 0:
            for app in app_list:
                data_list.append([app.unique_name, app.uuid[:8], utils.add_unicode_symbol_to_state(app.state),
                                  app.image_name, "%s (%d)" % (app.container_size, app.current_num_containers),
                                  utils.get_humanize_local_datetime_from_utc_datetime_string(app.deployed_datetime),
                                  app.web_public_dns])
                long_uuid_list.append(app.uuid)
        else:
            data_list.append(["", "", "", "", "", "", ""])
        if quiet:
            for uuid in long_uuid_list:
                print uuid
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print e


def application_details(identifiers):
    for identifier in identifiers:
        try:
            app_details = utils.fetch_app(identifier)
            print json.dumps(app_details.get_all_attributes(), indent=2)
        except Exception as e:
            print e


def app_start(identifiers):
    for identifier in identifiers:
        try:
            app_details = utils.fetch_app(identifier)
            result = app_details.start()
            if result:
                print app_details.uuid
        except Exception as e:
            print e


def app_stop(identifiers):
    for identifier in identifiers:
        try:
            app_details = utils.fetch_app(identifier)
            result = app_details.stop()
            if result:
                print app_details.uuid
        except Exception as e:
            print e


def app_terminate(identifiers):
    for identifier in identifiers:
        try:
            app_details = utils.fetch_app(identifier)
            result = app_details.delete()
            if result:
                print app_details.uuid
        except Exception as e:
            print e


def app_logs(identifiers):
    for identifier in identifiers:
        try:
            app_details = utils.fetch_app(identifier)
            print app_details.logs
        except Exception as e:
            print e


def app_scale(identifiers, target_num_containers):
    for identifier in identifiers:
        try:
            app_details = utils.fetch_app(identifier)
            if target_num_containers:
                app_details.target_num_containers = target_num_containers
                result = app_details.save()
                if result:
                    print app_details.uuid
        except Exception as e:
            print e


def app_alias(identifiers, dns):
    for identifier in identifiers:
        try:
            app_details = utils.fetch_app(identifier)
            if dns is not None:
                app_details.web_public_dns = dns
                result = app_details.save()
                if result:
                    print app_details.uuid
        except Exception as e:
            print e


def app_run(image, name, container_size, target_num_containers, run_command, entrypoint, container_ports,
            container_envvars, linked_to_application, autorestart, autoreplace, autodestroy, roles):
    try:
        ports = utils.parse_ports(container_ports)
        envvars = utils.parse_envvars(container_envvars)
        app = tutum.Application.create(image=image, name=name, container_size=container_size,
                                       target_num_containers=target_num_containers, run_command=run_command,
                                       entrypoint=entrypoint, container_ports=ports,
                                       container_envvars=envvars, linked_to_application=linked_to_application,
                                       autorestart=autorestart, autoreplace=autoreplace, autodestroy=autodestroy, roles=roles)
        result = app.save()
        if result:
            print app.uuid
    except Exception as e:
        print e


def ps(app_identifier, quiet=False, status=None):
    try:
        if app_identifier is None:
            containers = tutum.Container.list(state=status)
        elif utils.is_uuid4(app_identifier):
            containers = tutum.Container.list(application__uuid=app_identifier, state=status)
        else:
            containers = tutum.Container.list(application__name=app_identifier, state=status) + \
                         tutum.Container.list(application__uuid__startswith=app_identifier, state=status)
        headers = ["NAME", "UUID", "STATUS", "IMAGE", "RUN COMMAND", "SIZE", "EXIT CODE", "DEPLOYED", "PORTS"]
        data_list = []
        long_uuid_list = []
        if len(containers) != 0:
            for container in containers:
                ports_string = ""
                for index, port in enumerate(container.container_ports):
                    if port['outer_port'] is not None:
                        ports_string += "%s:%d->" % (container.public_dns, port['outer_port'])
                    ports_string += "%d/%s" % (port['inner_port'], port['protocol'])
                    if index != len(container.container_ports) - 1:
                        ports_string += ", "
                data_list.append([container.unique_name, container.uuid[:8],
                                  utils.add_unicode_symbol_to_state(container.state), container.image_name,
                                  container.run_command, container.container_size, container.exit_code,
                                  utils.get_humanize_local_datetime_from_utc_datetime_string(container.deployed_datetime),
                                  ports_string])
                long_uuid_list.append(container.uuid)
        else:
            data_list.append(["", "", "", "", "", "", "", "", ""])
        if quiet:
            for uuid in long_uuid_list:
                print uuid
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print e


def container_inspect(identifiers):
    for identifier in identifiers:
        try:
            container_details = utils.fetch_container(identifier)
            print json.dumps(container_details.get_all_attributes(), indent=2)
        except Exception as e:
            print e


def container_start(identifiers):
    for identifier in identifiers:
        try:
            container_details = utils.fetch_container(identifier)
            result = container_details.start()
            if result:
                print container_details.uuid
        except Exception as e:
            print e


def container_stop(identifiers):
    for identifier in identifiers:
        try:
            container_details = utils.fetch_container(identifier)
            result = container_details.stop()
            if result:
                print container_details.uuid
        except Exception as e:
            print e


def container_terminate(identifiers):
    for identifier in identifiers:
        try:
            container_details = utils.fetch_container(identifier)
            result = container_details.delete()
            if result:
                print container_details.uuid
        except Exception as e:
            print e


def container_logs(identifiers):
    for identifier in identifiers:
        try:
            container_details = utils.fetch_container(identifier)
            print container_details.logs
        except Exception as e:
            print e


def images(quiet=False, jumpstarts=False, linux=False):
    try:
        if jumpstarts:
            image_list = tutum.Image.list(starred=True)
        elif linux:
            image_list = tutum.Image.list(base_image=True)
        else:
            image_list = tutum.Image.list(is_private_image=True)
        headers = ["Name", "Description"]
        data_list = []
        name_list = []
        if len(image_list) != 0:
            for image in image_list:
                data_list.append([image.name, image.description])
                name_list.append(image.name)
        else:
            data_list.append(["", ""])

        if quiet:
            for name in name_list:
                print name
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print e


def add_image(repository, username, password, description):
    try:
        image = tutum.Image.create(name=repository, username=username, password=password, description=description)
        result = image.save()
        if result:
            print image.name
    except Exception as e:
        print e


def remove_image(repositories):
    for repository in repositories:
        try:
            image = tutum.Image.fetch(repository)
            result = image.delete()
            if result:
                print repository
        except Exception as e:
            print e


def update_image(repositories, username, password, description):
    for repository in repositories:
        try:
            image = tutum.Image.fetch(repository)
            if username is not None:
                image.username = username
            if password is not None:
                image.password = password
            if description is not None:
                image.description = description
            result = image.save()
            if result:
                print image.name
        except Exception as e:
            print e