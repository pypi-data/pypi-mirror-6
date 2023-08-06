import getpass
import ConfigParser
from os.path import join, expanduser
import pprint

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


def apps():
    try:
        app_list = tutum.Application.list()
        headers = ["Name", "UUID", "State", "Image", "Size", "Deployed datetime", "Web Hostname"]
        data_list = []
        if len(app_list) != 0:
            for app in app_list:
                data_list.append([app.unique_name, app.uuid[:8], app.state, app.image_tag, app.container_size,
                                  app.deployed_datetime, app.web_public_dns])
        else:
            data_list.append(["", "", "", "", "", "", ""])
        utils.tabulate_result(data_list, headers)
    except Exception as e:
        print e


def application_details(identifier):
    try:
        app_details = utils.fetch_app(identifier)
        pprint.pprint(app_details.get_all_attributes())
    except Exception as e:
        print e


def app_start(identifier):
    try:
        app_details = utils.fetch_app(identifier)
        result = app_details.start()
        if result:
            print app_details.uuid
    except Exception as e:
        print e


def app_stop(identifier):
    try:
        app_details = utils.fetch_app(identifier)
        result = app_details.stop()
        if result:
            print app_details.uuid
    except Exception as e:
        print e


def app_terminate(identifier):
    try:
        app_details = utils.fetch_app(identifier)
        result = app_details.delete()
        if result:
            print app_details.uuid
    except Exception as e:
        print e


def app_logs(identifier):
    try:
        app_details = utils.fetch_app(identifier)
        print app_details.logs
    except Exception as e:
        print e


def app_scale(identifier, target_num_containers):
    try:
        app_details = utils.fetch_app(identifier)
        if target_num_containers:
            app_details.target_num_containers = target_num_containers
            result = app_details.save()
            if result:
                print app_details.uuid
    except Exception as e:
        print e


def app_alias(identifier, dns):
    try:
        app_details = utils.fetch_app(identifier)
        if dns:
            app_details.web_public_dns = dns
            result = app_details.save()
            if result:
                print app_details.uuid
    except Exception as e:
        print e


def app_create(**kwargs):
    try:
        app = tutum.Application.create(**kwargs)
        result = app.save()
        if result:
            print app.uuid
    except Exception as e:
        print e


def ps(app_identifier):
    try:
        if app_identifier is None:
            containers = tutum.Container.list()
        elif utils.is_uuid4(app_identifier):
            containers = tutum.Container.list(application__uuid=app_identifier)
        else:
            containers = tutum.Container.list(application__name=app_identifier) + tutum.Container.list(application__uuid__startswith=app_identifier)
        headers = ["Name", "UUID", "State", "Image", "Run Command", "Size", "Exit Code", "Deployed datetime", "Ports"]
        data_list = []
        if len(containers) != 0:
            for container in containers:
                ports_string = ""
                for index, port in enumerate(container.container_ports):
                    if port['outer_port'] is not None:
                        ports_string += "%s:%d->" % (container.public_dns, port['outer_port'])
                    ports_string += "%d/%s" % (port['inner_port'], port['protocol'])
                    if index != len(container.container_ports) - 1:
                        ports_string += ", "
                data_list.append([container.unique_name, container.uuid[:8], container.state, container.image_tag,
                                  container.run_command, container.container_size, container.exit_code,
                                  container.deployed_datetime, ports_string])
        else:
            data_list.append(["", "", "", "", "", "", "", "", ""])
        utils.tabulate_result(data_list, headers)
    except Exception as e:
        print e


def container_inspect(identifier):
    try:
        container_details = utils.fetch_container(identifier)
        pprint.pprint(container_details.get_all_attributes())
    except Exception as e:
        print e


def container_start(identifier):
    try:
        container_details = utils.fetch_container(identifier)
        result = container_details.start()
        if result:
            print container_details.uuid
    except Exception as e:
        print e


def container_stop(identifier):
    try:
        container_details = utils.fetch_container(identifier)
        result = container_details.stop()
        if result:
            print container_details.uuid
    except Exception as e:
        print e


def container_terminate(identifier):
    try:
        container_details = utils.fetch_container(identifier)
        result = container_details.delete()
        if result:
            print container_details.uuid
    except Exception as e:
        print e


def container_logs(identifier):
    try:
        container_details = utils.fetch_container(identifier)
        print container_details.logs
    except Exception as e:
        print e