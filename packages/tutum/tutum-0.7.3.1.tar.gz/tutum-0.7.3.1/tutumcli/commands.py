import getpass
import ConfigParser
import json
import requests
import sys
import urlparse
import webbrowser
import yaml
import re
from os.path import join, expanduser, abspath, isfile

from tutum.api import auth
from tutum.api import exceptions
import tutum

from tutumcli import utils
from tutumcli.exceptions import ObjectNotFound, DockerNotFound


TUTUM_FILE = '.tutum'
AUTH_SECTION = 'auth'
USER_OPTION = "user"
APIKEY_OPTION = 'apikey'

TUTUM_AUTH_ERROR_EXIT_CODE = 2
EXCEPTION_EXIT_CODE = 3


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
        registered, text = try_register(username, password)
        if registered:
            print text
        else:
            if 'username: A user with that username already exists.' in text:
                print "Wrong username and/or password. Please try to login again"
                sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)
            text = text.replace('password1', 'password')
            text = text.replace('password2', 'password')
            text = text.replace('\npassword: This field is required.', '', 1)
            print text
            sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)
    except Exception as e:
        print e
        sys.exit(EXCEPTION_EXIT_CODE)


def try_register(username, password):
    import tutum_cli

    email = raw_input("Email: ")

    headers = {"Content-Type": "application/json", "User-Agent": "tutum/%s" % tutum_cli.VERSION}
    data = {'username': username, "password1": password, "password2": password, "email": email}

    r = requests.post(urlparse.urljoin(tutum.base_url, "register/"), data=json.dumps(data), headers=headers)

    try:
        if r.status_code == 201:
            return True, "Account created. Please check your email for activation instructions."
        elif r.status_code == 429:
            return False, "Too many retries. Please login again later."
        else:
            messages = r.json()['register']
            if isinstance(messages,dict):
                text = []
                for key in messages.keys():
                    text.append("%s: %s" % (key, '\n'.join(messages[key])))
                text = '\n'.join(text)
            else:
                text = messages
            return False, text
    except:
        return False, r.text


def search(text):
    try:
        docker_client = utils.get_docker_client()
        results = docker_client.search(text)
        headers = ["NAME", "DESCRIPTION", "STARS", "OFFICIAL", "TRUSTED"]
        data_list = []
        if len(results) != 0:
            for result in results:
                description = result["description"].replace("\n", "\\n")
                description = description[:80] + " [...]" if len(result["description"]) > 80 else description
                data_list.append([result["name"], description
                                  , str(result["star_count"]),
                                  u"\u2713" if result["is_official"] else "",
                                  u"\u2713" if result["is_trusted"] else ""])
        else:
            data_list.append(["", "", "", "", ""])
        utils.tabulate_result(data_list, headers)
    except Exception as e:
        print e
        sys.exit(EXCEPTION_EXIT_CODE)


def open_app():
    try:
        app_list = tutum.Application.list()
        deployed_datetimes = {}
        for app in app_list:
            if app.web_public_dns and app.state in ["Running", "Partly running"]:
                deployed_datetimes[utils.from_utc_string_to_utc_datetime(app.deployed_datetime)] = app.web_public_dns
        if deployed_datetimes:
            max_datetime = max(deployed_datetimes.keys())
            webbrowser.open("http://" + deployed_datetimes[max_datetime])
        else:
            print "Error: There are not web applications Running or Partly Running"
    except Exception as e:
        print e
        sys.exit(EXCEPTION_EXIT_CODE)


def apps(quiet=False, status=None, remote=False, local=False):
    try:
        headers = ["NAME", "UUID", "STATUS", "IMAGE", "SIZE (#)", "DEPLOYED", "WEB HOSTNAME"]

        print_headers = True
        current_apps = {}
        try:
            current_apps = utils.get_current_apps_and_its_containers()
        except DockerNotFound:
            print_headers = False

        if not local:
            app_list = tutum.Application.list(state=status)
            data_list = []
            long_uuid_list = []
            for app in app_list:
                data_list.append([app.unique_name, app.uuid[:8], utils.add_unicode_symbol_to_state(app.state),
                                  app.image_name, "%s (%d)" % (app.container_size, app.current_num_containers),
                                  utils.get_humanize_local_datetime_from_utc_datetime_string(app.deployed_datetime),
                                  app.web_public_dns])
                long_uuid_list.append(app.uuid)
            if len(data_list) == 0:
                data_list.append(["", "", "", "", "", "", ""])

            if quiet:
                for uuid in long_uuid_list:
                    print uuid
            else:
                if print_headers:
                    print "---- APPS IN TUTUM ----"
                utils.tabulate_result(data_list, headers)
                if not remote:
                    print

        if not remote and print_headers:
            data_list = []
            name_list = []
            for current_app, app_config in current_apps.iteritems():
                if not status or status == app_config["status"]:
                    data_list.append([current_app, app_config["uuid"],
                                      utils.add_unicode_symbol_to_state(app_config["status"]),
                                      app_config["image"],
                                      "%s (%d)" % (app_config["container_size"], len(app_config["containers"])),
                                      utils.get_humanize_local_datetime_from_utc_datetime(app_config["deployed"]),
                                      app_config["web_hostname"]])
                    name_list.append(current_app)

            if len(data_list) == 0:
                data_list.append(["", "", "", "", "", "", ""])

            if quiet:
                for uuid in name_list:
                    print uuid
            else:
                print "---- LOCAL APPS ----"
                utils.tabulate_result(data_list, headers)
    except Exception as e:
        print e
        sys.exit(EXCEPTION_EXIT_CODE)


def details(identifiers):
    for identifier in identifiers:
        try:
            is_remote, is_app, app_or_container = utils.launch_queries_in_parallel(identifier)
            if is_remote:
                if is_app:
                    print json.dumps(tutum.Application.fetch(app_or_container.uuid).get_all_attributes(), indent=2)
                else:
                    print json.dumps(tutum.Container.fetch(app_or_container.uuid).get_all_attributes(), indent=2)
            else:
                print json.dumps(utils.details_local_object(app_or_container), indent=2, cls=utils.JsonDatetimeEncoder)
        except Exception as e:
            print e


def start(identifiers):
    for identifier in identifiers:
        try:
            is_remote, is_app, app_or_container = utils.launch_queries_in_parallel(identifier)
            if is_remote:
                result = app_or_container.start()
                if result:
                    print app_or_container.uuid
            else:
                print utils.start_local_object(app_or_container)
        except Exception as e:
            print e


def stop(identifiers):
    for identifier in identifiers:
        try:
            is_remote, is_app, app_or_container = utils.launch_queries_in_parallel(identifier)
            if is_remote:
                result = app_or_container.stop()
                if result:
                    print app_or_container.uuid
            else:
                print utils.stop_local_object(app_or_container)
        except Exception as e:
            print e


def terminate(identifiers):
    for identifier in identifiers:
        try:
            is_remote, is_app, app_or_container = utils.launch_queries_in_parallel(identifier)
            if is_remote:
                result = app_or_container.delete()
                if result:
                    print app_or_container.uuid
            else:
                print utils.terminate_local_object(app_or_container)
        except Exception as e:
            print e


def logs(identifiers):
    for identifier in identifiers:
        try:
            is_remote, is_app, app_or_container = utils.launch_queries_in_parallel(identifier)
            if is_remote:
                print app_or_container.logs
            else:
                print utils.logs_local_object(app_or_container)
        except Exception as e:
            print e


def app_scale(identifiers, target_num_containers):
    for identifier in identifiers:
        try:
            is_remote, app_details = utils.fetch_app(identifier)

            if is_remote:
                if target_num_containers:
                    app_details.target_num_containers = target_num_containers
                    result = app_details.save()
                    if result:
                        print app_details.uuid
            else:
                image = utils.parse_image_name(app_details[identifier]["image"])
                tag = image["tag"] if image["tag"] else "latest"
                #if we found a local image, at least has one container
                app = app_details[identifier]

                num_containers = target_num_containers - len(app["containers"])

                if num_containers > 0:

                    container_names = utils.get_containers_unique_names(identifier,
                                                                        [container["name"]
                                                                         for container in app["containers"]],
                                                                        num_containers)
                    ports = utils.parse_ports(utils.get_ports_from_image(image["full_name"], tag))
                    ports += utils.get_port_list_from_string(app["containers"][0]["ports"])

                    already_deployed = {}
                    for container in app["containers"]:
                        already_deployed[container["name"]] = container["name"] + "-link"
                    utils.create_containers_for_an_app(image["full_name"],
                                                       image["tag"],
                                                       container_names,
                                                       app["containers"][0]["run_command"],
                                                       app["containers"][0]["entrypoint"],
                                                       app["containers"][0]["size"],
                                                       ports,
                                                       app["containers"][0]["envvars"],
                                                       already_deployed)
                elif num_containers < 0:
                    containers_to_destroy = min(len(app["containers"]), abs(num_containers))
                    for i in range(containers_to_destroy):
                        try:
                            utils.terminate_local_object(app["containers"][i])
                        except Exception as e:
                            print e
                            pass
                print identifier
        except Exception as e:
            print e


def app_alias(identifiers, dns):
    for identifier in identifiers:
        try:
            app_details = utils.fetch_remote_app(identifier)
            if dns is not None:
                app_details.web_public_dns = dns
                result = app_details.save()
                if result:
                    print app_details.uuid
        except Exception as e:
            print e


def app_run(image, name, container_size, target_num_containers, run_command, entrypoint, container_ports,
            container_envvars, linked_to_applications, autorestart, autoreplace, autodestroy, roles, local):
    try:
        ports = utils.parse_ports(container_ports)
        envvars = utils.parse_envvars(container_envvars)

        if local:
            image_options = utils.parse_image_name(image)
            tag = image_options["tag"] if image_options["tag"] else "latest"
            image_ports = utils.parse_ports(utils.get_ports_from_image(image_options["full_name"], tag))
            ports += image_ports
            app_name, container_names = utils.get_app_and_containers_unique_name("local-"+name if name else
                                                                                 utils.TUTUM_LOCAL_CONTAINER_NAME %
                                                                                 image_options["short_name"],
                                                                                 target_num_containers)
            already_deployed = {}
            if linked_to_applications:
                for link in linked_to_applications:
                    is_app, app = utils.fetch_local_app_container(link)
                    if is_app:
                        for container in app[link]["containers"]:
                            already_deployed[container["name"]] = container["name"] + "-link"
                    else:
                        raise ObjectNotFound("Cannot find a local application with the identifier '%s'" % link)

            _ = utils.create_containers_for_an_app(image_options["full_name"],
                                                   tag,
                                                   container_names,
                                                   run_command,
                                                   entrypoint,
                                                   container_size,
                                                   ports,
                                                   dict((envvar["key"], envvar["value"]) for envvar in envvars),
                                                   already_deployed)
            print app_name
        else:
            app = tutum.Application.create(image=image, name=name, container_size=container_size,
                                           target_num_containers=target_num_containers, run_command=run_command,
                                           entrypoint=entrypoint, container_ports=ports,
                                           container_envvars=envvars, linked_to_application=linked_to_applications,
                                           autorestart=autorestart, autoreplace=autoreplace, autodestroy=autodestroy,
                                           roles=roles)
            result = app.save()
            if result:
                print app.uuid
    except Exception as e:
        print e
        sys.exit(EXCEPTION_EXIT_CODE)


def ps(app_identifier, quiet=False, status=None, remote=False, local=False):
    try:
        headers = ["NAME", "UUID", "STATUS", "IMAGE", "RUN COMMAND", "SIZE", "EXIT CODE", "DEPLOYED", "PORTS"]

        print_headers = True
        current_apps = {}
        try:
            current_apps = utils.get_current_apps_and_its_containers()
        except DockerNotFound:
            print_headers = False

        if not local:
            if app_identifier is None:
                containers = tutum.Container.list(state=status)
            elif utils.is_uuid4(app_identifier):
                containers = tutum.Container.list(application__uuid=app_identifier, state=status)
            else:
                containers = tutum.Container.list(application__name=app_identifier, state=status) + \
                             tutum.Container.list(application__uuid__startswith=app_identifier, state=status)

            data_list = []
            long_uuid_list = []

            for container in containers:
                ports = []
                for index, port in enumerate(container.container_ports):
                    ports_string = ""
                    if port['outer_port'] is not None:
                        ports_string += "%s:%d->" % (container.public_dns, port['outer_port'])
                    ports_string += "%d/%s" % (port['inner_port'], port['protocol'])
                    ports.append(ports_string)

                ports_string = ", ".join(ports)
                data_list.append([container.unique_name, container.uuid[:8],
                                  utils.add_unicode_symbol_to_state(container.state), container.image_name,
                                  container.run_command, container.container_size, container.exit_code,
                                  utils.get_humanize_local_datetime_from_utc_datetime_string(container.deployed_datetime),
                                  ports_string])
                long_uuid_list.append(container.uuid)
            if len(data_list) == 0:
                data_list.append(["", "", "", "", "", "", "", "", ""])

            if quiet:
                for uuid in long_uuid_list:
                    print uuid
            else:
                if print_headers:
                    print "---- CONTAINERS IN TUTUM ----"
                utils.tabulate_result(data_list, headers)
                if not remote:
                    print

        if not remote and print_headers:
            data_list = []
            long_uuid_list = []
            for current_app, app_config in current_apps.iteritems():
                if not app_identifier or app_identifier in [app_config["uuid"], current_app]:
                    for container in app_config["containers"]:
                        if not status or status == container["status"]:
                            data_list.append([container["name"], container["uuid"][:8],
                                              utils.add_unicode_symbol_to_state(container["status"]),
                                              container["image"], container["run_command"], container["size"],
                                              container["exit_code"],
                                              utils.get_humanize_local_datetime_from_utc_datetime(container["deployed"]),
                                              container["ports"]])
                            long_uuid_list.append(container["uuid"])
            if len(data_list) == 0:
                data_list.append(["", "", "", "", "", "", "", "", ""])

            if quiet:
                for uuid in long_uuid_list:
                    print uuid
            else:
                print "---- LOCAL CONTAINERS ----"
                utils.tabulate_result(data_list, headers)

    except Exception as e:
        print e
        sys.exit(EXCEPTION_EXIT_CODE)


def build(image_name, working_directory, quiet, nocache):
    try:
        directory = abspath(working_directory)
        dockerfile_path = join(directory, "Dockerfile")

        if not isfile(dockerfile_path):
            procfile_path = join(directory, "Procfile")
            ports = ""
            process = ''
            if isfile(procfile_path):
                cmd = ['"/start"']
                with open(procfile_path) as procfile:
                    dataMap = yaml.load(procfile)
                if len(dataMap) > 1:
                    while not process or (not process in dataMap):
                        process = raw_input("Process type to build, %s: " % dataMap.keys())
                    process = '"%s"' % process

                if (len(dataMap) == 1 and 'web' in dataMap) or (process == 'web'):
                    ports = "80"
                    process = '"web"'

                cmd.append(process)

            else:
                while not process:
                    process = raw_input("Run command: ")
                cmd = process

            if process != '"web"':
                port_regexp = re.compile('^\d{1,5}(\s\d{1,5})*$')
                while not ports or not bool(port_regexp.match(ports)):
                    ports = raw_input("Exposed Ports (ports separated by whitespace) i.e. 80 8000: ") or ""

            utils.build_dockerfile(dockerfile_path, ports, cmd)

        docker_client = utils.get_docker_client()
        output = docker_client.build(path=directory, tag=image_name, quiet=quiet, nocache=nocache, rm=True)
        for line in output:
            if not quiet:
                utils.print_stream_line(line)
        print image_name
    except Exception as e:
        print e
        sys.exit(EXCEPTION_EXIT_CODE)


def images(quiet=False, jumpstarts=False, linux=False, local=False, remote=False):
    try:
        if not local:
            headers = ["NAME", "DESCRIPTION"]
            data_list = []
            name_list = []
            if jumpstarts:
                image_list = tutum.Image.list(starred=True)
            elif linux:
                image_list = tutum.Image.list(base_image=True)
            else:
                image_list = tutum.Image.list(is_private_image=True)
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
                print "---- REMOTE IMAGES IN TUTUM ----"
                utils.tabulate_result(data_list, headers)
                if not remote:
                    print

        if not remote and not (linux or jumpstarts):
            headers = ["NAME", "ID", "CREATED", "PARENT ID", "VIRTUAL SIZE", "SIZE"]
            docker_client = utils.get_docker_client()
            local_images = docker_client.images(quiet=quiet)
            data_list = []

            if not quiet:
                if len(local_images) != 0:
                    for repotags in local_images:
                        for repotag in repotags["RepoTags"]:
                            data_list.append([repotag, repotags["Id"],
                                              utils.get_humanize_local_datetime_from_utc_datetime(
                                                  utils.from_utc_timestamp_to_utc_datetime(int(repotags["Created"]))),
                                              repotags["ParentId"],
                                              repotags["VirtualSize"],
                                              repotags["Size"]])
                else:
                    data_list.append(["", "", "", "", "", ""])
                print "---- LOCAL IMAGES ----"
                utils.tabulate_result(data_list, headers)
            else:
                for uuid in local_images:
                    print uuid


    except Exception as e:
        print e
        sys.exit(EXCEPTION_EXIT_CODE)


def add_image(repository, username, password, description):
    try:
        image = tutum.Image.create(name=repository, username=username, password=password, description=description)
        result = image.save()
        if result:
            print image.name
    except Exception as e:
        print e
        sys.exit(EXCEPTION_EXIT_CODE)


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

def push(name, public):

    AUTH_ERROR = 'auth_error'
    NO_ERROR = 'no_error'

    def print_stream_line(output):

        if "}{" in output:
            lines = output.replace('}{', '}}{{').split('}{')
        else:
            lines = [output]
        last_id = None
        for line in lines:
            formatted_output = ''
            try:
                obj = json.loads(line)
                status = obj.get('status', None)
                id = obj.get('id', None)
                progress = obj.get('progress', None)
                error = obj.get('error',None)

                if error:
                    print ''
                    print error
                    sys.exit(EXCEPTION_EXIT_CODE)

                if status and id and progress:
                    if id != last_id:
                        formatted_output = '\n%s: %s %s' % (id, status, progress)
                    else:
                        formatted_output = '\r%s: %s %s\033[K' % (id, status, progress)

                elif status and id:
                    if id != last_id:
                        formatted_output = '\n%s: %s' % (id, status)
                    else:
                        formatted_output = '\r%s: %s\033[K' % (id, status)
                else:
                    formatted_output = '\n%s' % status
            except ValueError:
                print line
                sys.exit(EXCEPTION_EXIT_CODE)
            last_id = id

            sys.stdout.write(formatted_output)
            sys.stdout.flush()

    def push_to_public(repository):
        print 'Pushing %s to public registry ...' % repository

        output_stream = docker_client.push(repository, stream=True)
        output_status = NO_ERROR
        for line in output_stream:
            if 'status 401' in line.lower():
                output_status = AUTH_ERROR
                continue
            print_stream_line(line)

        if output_status == NO_ERROR:
            print ''
            sys.exit()

        if output_status == AUTH_ERROR:
            print 'Please login prior to push:'
            username = raw_input('Username: ')
            password = getpass.getpass()
            email = raw_input('Email: ')
            try:
                result = docker_client.login(username, password=password, email=email)
                if isinstance(result, dict):
                    print result.get('Status', None)
            except Exception as e:
                print e
                sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)
            push_to_public(repository)

    def push_to_tutum(repository):
        print 'Pushing %s to Tutum private registry ...' % repository

        user = tutum.user
        apikey = tutum.apikey
        if user is None or apikey is None:
            print 'Not authorized'
            sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)

        try:
            docker_client.login(user, apikey, registry='https://r.tutum.co/v1/')
        except Exception as e:
            print e
            sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)

        if repository:
            repository = filter(None, repository.split('/'))[-1]
        repository = 'r.tutum.co/%s/%s' % (user, repository)

        try:
            print 'Tagging %s as %s ...' % (name, repository)
            docker_client.tag(name, repository)
        except Exception as e:
            print e
            sys.exit(EXCEPTION_EXIT_CODE)

        output_stream = docker_client.push(repository, stream=True)
        for line in output_stream:
            print_stream_line(line)
        print ''

    docker_client = utils.get_docker_client()
    if public:
        push_to_public(name)
    else:
        push_to_tutum(name)
