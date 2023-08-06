import datetime
import re
import multiprocessing
import json

from tabulate import tabulate
import tutum
from dateutil import tz
import ago
import docker
from os import getenv

from tutumcli.exceptions import NonUniqueIdentifier, ObjectNotFound, BadParameter, DockerNotFound, PublicImageNotFound

TUTUM_LOCAL_PREFIX = "local-"
TUTUM_LOCAL_CONTAINER_NAME = TUTUM_LOCAL_PREFIX + "%s"

CONTAINER_SIZE = {
        "XS": {"cpu_shares": 256, "memory": 268435456},
        "S": {"cpu_shares": 512, "memory": 536870912},
        "M": {"cpu_shares": 1024, "memory": 1073741824},
        "L": {"cpu_shares": 2048, "memory": 2147483648},
        "XL": {"cpu_shares": 4096, "memory": 4294967286}
}


def tabulate_result(data_list, headers):
    print tabulate(data_list, headers, stralign="left", tablefmt="plain")


def from_utc_string_to_utc_datetime(utc_datetime_string):
    if not utc_datetime_string:
        return None
    utc_date_object = datetime.datetime.strptime(utc_datetime_string, "%a, %d %b %Y %H:%M:%S +0000")

    return utc_date_object


def from_utc_timestamp_to_utc_datetime(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


def get_humanize_local_datetime_from_utc_datetime_string(utc_datetime_string):
    utc_target_datetime = from_utc_string_to_utc_datetime(utc_datetime_string)
    return get_humanize_local_datetime_from_utc_datetime(utc_target_datetime)


def get_humanize_local_datetime_from_utc_datetime(utc_target_datetime):
    local_now = datetime.datetime.now(tz.tzlocal())
    if utc_target_datetime:
        local_target_datetime = utc_target_datetime.replace(tzinfo=tz.gettz("UTC")).astimezone(tz=tz.tzlocal())
        return ago.human(local_now - local_target_datetime, precision=1)
    return ""


def is_uuid4(identifier):
    uuid4_regexp = re.compile('^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}', re.I)
    match = uuid4_regexp.match(identifier)
    return bool(match)


def fetch_remote_container(identifier, raise_exceptions=True):

    try:
        if is_uuid4(identifier):
            try:
                return tutum.Container.fetch(identifier)
            except Exception:
                raise ObjectNotFound("Cannot find a container with the identifier '%s'" % identifier)
        else:
            objects_same_identifier = tutum.Container.list(unique_name=identifier) or \
                                      tutum.Container.list(uuid__startswith=identifier)
            if len(objects_same_identifier) == 1:
                return objects_same_identifier[0]
            elif len(objects_same_identifier) == 0:
                raise ObjectNotFound("Cannot find a container with the identifier '%s'" % identifier)
            raise NonUniqueIdentifier("More than one container has the same identifier, please use the long uuid")

    except (NonUniqueIdentifier, ObjectNotFound) as e:
        if not raise_exceptions:
                return e
        raise e


def fetch_remote_app(identifier, raise_exceptions=True):

    try:
        if is_uuid4(identifier):
            try:
                return tutum.Application.fetch(identifier)
            except Exception:
                raise ObjectNotFound("Cannot find an application with the identifier '%s'" % identifier)
        else:
            objects_same_identifier = tutum.Application.list(unique_name=identifier) or \
                                      tutum.Application.list(uuid__startswith=identifier)
            if len(objects_same_identifier) == 1:
                return objects_same_identifier[0]
            elif len(objects_same_identifier) == 0:
                raise ObjectNotFound("Cannot find an application with the identifier '%s'" % identifier)
            raise NonUniqueIdentifier("More than one application has the same identifier, please use the long uuid")
    except (NonUniqueIdentifier, ObjectNotFound) as e:
        if not raise_exceptions:
                return e
        raise e


def fetch_local_app_container(identifier, raise_exceptions=True):
    try:
        current_apps_and_containers = get_current_apps_and_its_containers()

        identified_containers = []
        identified_apps = []

        for app, app_config in current_apps_and_containers.iteritems():
            if app == identifier:
                identified_apps.append({app: app_config})

            for container in app_config["containers"]:
                if container["uuid"].startswith(identifier) or container["name"] == identifier:
                    identified_containers.append(container)

        if len(identified_apps) == len(identified_containers) == 0:
            raise ObjectNotFound("Cannot find an application or a container with identifier '%s'" % identifier)
        elif len(identified_containers) > 1 or \
                        len(identified_apps) > 1 or \
                (len(identified_apps) == len(identified_containers)):
            raise NonUniqueIdentifier("Identifier '%s' is being used by more than one container and/or application, "
                                      "please use the long uuid" % identifier)
        elif len(identified_apps) == 1:
            return True, identified_apps[0]
        elif len(identified_containers) == 1:
            return False, identified_containers[0]
    except DockerNotFound:
        if not raise_exceptions:
                return None, \
                       ObjectNotFound("Cannot find an application or a container with identifier '%s'" % identifier)
        raise ObjectNotFound("Cannot find an application or a container with identifier '%s'" % identifier)
    except (NonUniqueIdentifier, ObjectNotFound) as e:
        if not raise_exceptions:
                return None, e
        raise e


def fetch_app(identifier):
    remote = fetch_remote_app(identifier, False)
    is_app, local = fetch_local_app_container(identifier, False)

    if all([isinstance(remote, ObjectNotFound), isinstance(local, ObjectNotFound)]) or \
            (isinstance(remote, ObjectNotFound) and not isinstance(local, Exception) and
             not is_app):
        raise ObjectNotFound("Cannot find an application with the identifier '%s'" % identifier)
    elif any([isinstance(remote, NonUniqueIdentifier), isinstance(local, NonUniqueIdentifier)]) or \
            sum([not isinstance(result, Exception) for result in [remote, local]]) > 1 and is_app:
        raise NonUniqueIdentifier("Identifier '%s' is being used by more than one container and/or application, "
                                  "please use the long uuid" % identifier)

    if not isinstance(remote, ObjectNotFound):
        return True, remote

    elif not isinstance(local, ObjectNotFound):
        return False, local


def parse_ports(port_list):
    parsed_ports = []
    if port_list is not None:
        parsed_ports = []
        for port in port_list:
            parsed_ports.append(_get_port_dict(port))
    return parsed_ports


def _get_port_dict(port):
    port_regexp = re.compile('^[0-9]{1,5}/(tcp|udp)$')
    match = port_regexp.match(port)
    if bool(match):
        port = port.split("/", 1)
        inner_port = int(port[0])
        protocol = port[1].lower()
        return {'protocol': protocol, 'inner_port': inner_port}
    raise BadParameter("Port argument %s does not match with 'port/protocol'. Example: 80/tcp" % port)


def parse_envvars(envvar_list):
    parsed_envvars = []
    if envvar_list is not None:
        for envvar in envvar_list:
            parsed_envvars.append(_is_envvar(envvar))
    return parsed_envvars


def _is_envvar(envvar):
    envvar_regexp = re.compile('^[a-zA-Z_]+[a-zA-Z0-9_]*=[^?!=]+$')
    match = envvar_regexp.match(envvar)
    if bool(match):
        envvar = envvar.split("=", 1)
        return {'key': envvar[0], 'value': envvar[1]}
    raise BadParameter("Environment Variable argument %s does not match with 'KEY=VALUE'. Example: ENVVAR=foo" % envvar)


def add_unicode_symbol_to_state(state):
    if state in ["Running", "Partly running"]:
        return u"\u25B6 " + state
    elif state in ["Init", "Stopped"]:
        return u"\u25FC " + state
    elif state in ["Starting", "Stopping", "Scaling", "Terminating"]:
        return u"\u2699 " + state
    elif state in ["Start failed", "Stopped with errors"]:
        return u"\u0021 " + state
    elif state == "Terminated":
        return u"\u2718 " + state
    return state


def launch_queries_in_parallel(identifier):

    pool = multiprocessing.Pool(processes=2)
    apps_result = pool.apply_async(fetch_remote_app, (identifier, False, ))
    containers_result = pool.apply_async(fetch_remote_container, (identifier, False, ))
    pool.close()
    pool.join()

    app = apps_result.get()
    container = containers_result.get()
    is_app, local_result = fetch_local_app_container(identifier, False)

    if all([isinstance(app, ObjectNotFound),
            isinstance(container, ObjectNotFound),
            isinstance(local_result, ObjectNotFound)]):
        raise ObjectNotFound("Cannot find an application or a container with identifier '%s'" % identifier)
    elif any([isinstance(app, NonUniqueIdentifier),
              isinstance(container, NonUniqueIdentifier),
              isinstance(local_result, NonUniqueIdentifier)]) or \
            sum([not isinstance(result, Exception) for result in [app, container, local_result]]) > 1:
        raise NonUniqueIdentifier("Identifier '%s' is being used by more than one container and/or application, "
                                  "please use the long uuid" % identifier)
    elif not isinstance(app, ObjectNotFound):
        return True, True, app

    elif not isinstance(container, ObjectNotFound):
        return True, False, container

    elif not isinstance(local_result, ObjectNotFound):
        return False, is_app, local_result

    return None, None


def get_docker_client():
    try:
        docker_client = docker.Client(base_url=getenv("DOCKER_HOST"))
        docker_client.version()
        return docker_client
    except Exception:
        raise DockerNotFound("Cannot connect to docker (is it running?)")


def parse_image_name(image_name):
    regexp = r"^(?P<full_name>((?P<registry_host>[a-z0-9\.\-]+\.[a-z0-9\.\-]+)/)?" \
             r"(?P<name_without_host>((?P<namespace>[a-z0-9\.\-]+)/)?" \
             r"(?P<short_name>[a-z0-9\.\-_]+)))(:(?P<tag>[a-z0-9\.\-]+))?$"
    if not re.search(regexp, str(image_name)):
        raise Exception("Invalid image name")
    parsed_results = re.match(regexp, str(image_name)).groupdict()
    parsed_results["index"] = "index.docker.io"
    return parsed_results


def get_app_and_containers_unique_name(name, num_containers=1):
    current_apps = get_current_apps_and_its_containers()
    similar_names = {}

    for app_name, config in current_apps.iteritems():
        if app_name.startswith(name):
            similar_names[app_name] = config["containers"]

    app_name = None
    if not name in similar_names:
        app_name = name
    else:
        i = 1
        while not app_name:
            new_name = name + "-" + str(i)
            if not new_name in similar_names:
                app_name = new_name
                break
            i += 1
    return app_name, get_containers_unique_names(app_name, [], num_containers)


def get_containers_unique_names(app_name, current_containers, num_containers=1):
    container_names = []
    for i in range(num_containers):
        i = 1
        container_name = None
        while not container_name:
            new_name = app_name + "-" + str(i)
            if not new_name in current_containers and not new_name in container_names:
                container_name = new_name
                container_names.append(container_name)
            i += 1
    return container_names


def get_current_apps_and_its_containers():
    docker_client = get_docker_client()
    stopped_running_containers = docker_client.containers(all=True, quiet=True)
    current_apps = {}
    deployed_datetime = datetime.datetime.utcnow()

    for container in stopped_running_containers:
        inspected_container = docker_client.inspect_container(container["Id"])
        app_name = get_app_name_from_container_name(inspected_container['Name'][1:])
        size_by_cpu = get_size_from_cpu_shares(inspected_container["Config"]["CpuShares"])
        size_by_memory = get_size_from_memory(inspected_container["Config"]["Memory"])

        if not app_name or not size_by_cpu or not size_by_memory or size_by_cpu != size_by_memory:
            #it is not a tutum container
            continue
        app_config = current_apps.get(app_name, {"uuid": "", "status": "",
                                                 "image": inspected_container["Config"]["Image"],
                                                 "container_size": size_by_cpu,
                                                 "deployed": "",
                                                 "web_hostname": "", "containers": []})

        container_status = "Running" if inspected_container["State"]["Running"] else "Stopped"
        if container_status == "Stopped" and inspected_container["State"]["ExitCode"] != 0:
            container_status = "Stopped with errors"
        container_config = {"app_name": app_name,
                            "name": inspected_container['Name'][1:],
                            "uuid": inspected_container["ID"],
                            "status": container_status,
                            "image": inspected_container["Config"]["Image"],
                            "run_command": " ".join(inspected_container["Config"]["Cmd"])
                            if inspected_container["Config"]["Cmd"] else "",
                            "entrypoint": " ".join(inspected_container["Config"]["Entrypoint"])
                            if inspected_container["Config"]["Entrypoint"] else "",
                            "size": size_by_cpu,
                            "exit_code": inspected_container["State"]["ExitCode"],
                            "envvars": inspected_container["Config"]["Env"],
                            "deployed": datetime.datetime.strptime(inspected_container["Created"].split(".")[0],
                                                                   "%Y-%m-%dT%H:%M:%S")}
        ports = []
        if inspected_container["HostConfig"]["PortBindings"] is not None:
            for port, bindings in inspected_container["HostConfig"]["PortBindings"].iteritems():
                port_number_protocol = port.split("/")
                for binding in bindings:
                    port_definition = "%s:%s->%s/%s" % \
                                      (binding["HostIp"],
                                       binding["HostPort"],
                                       port_number_protocol[0],
                                       port_number_protocol[1])
                    ports.append(port_definition)

        ports = ", ".join(ports) if ports else ""
        container_config["ports"] = ports
        app_config["containers"].append(container_config)

        app_config["deployed"] = container_config["deployed"] \
            if container_config["deployed"] < deployed_datetime else deployed_datetime

        current_apps[app_name] = app_config

    for app, app_config in current_apps.iteritems():
        current_apps[app]["status"] = _calculate_local_app_status(app_config["containers"])

    return current_apps


def get_app_name_from_container_name(container_local_name):
    local_name_regexp = re.compile('^local\-([a-zA-Z0-9_\-]+)\-([0-9]+)$')
    match = local_name_regexp.match(container_local_name)
    if bool(match):
        split_name = container_local_name.split("-")
        return "-".join(split_name[:-1])
    return None


def get_size_from_cpu_shares(cpu_shares_value):
    for size, config in CONTAINER_SIZE.iteritems():
        if config["cpu_shares"] == cpu_shares_value:
            return size
    return None


def get_size_from_memory(memory_value):
    for size, config in CONTAINER_SIZE.iteritems():
        if config["memory"] == memory_value:
            return size
    return None


def _calculate_local_app_status(container_list):
    all_status = {}

    for container in container_list:
        number = all_status.get(container["status"], 0)
        all_status[container["status"]] = number + 1

    if all_status.get("Running", 0) != 0:
        if all_status.get("Stopped", 0) == all_status.get("Stopped with errors", 0) == 0:
            return "Running"
        else:
            return "Partly running"
    else:
        if all_status.get("Stopped", 0) == 0 and all_status.get("Stopped with errors", 0) != 0:
            return "Stopped with errors"
        else:
            return "Stopped"


def _start_local_container(container):
    docker_client = get_docker_client()
    docker_client.restart(container["uuid"])


def start_local_object(local_object):
    if is_local_object_an_app(local_object):
        # is an app
        containers = local_object.values()[0]["containers"]
        for container in containers:
            _start_local_container(container)
        return containers[0]["app_name"]
    else:
        # is a container
        _start_local_container(local_object)
        return local_object["uuid"]


def _stop_local_container(container):
    docker_client = get_docker_client()
    docker_client.stop(container["uuid"])


def stop_local_object(local_object):
    if is_local_object_an_app(local_object):
        # is an app
        containers = local_object.values()[0]["containers"]
        for container in containers:
            _stop_local_container(container)
        return containers[0]["app_name"]
    else:
        # is a container
        _stop_local_container(local_object)
        return local_object["uuid"]


def _terminate_local_container(container):
    docker_client = get_docker_client()
    try:
        docker_client.remove_container(container["uuid"])
    except Exception:
        docker_client.kill(container["uuid"])
        docker_client.remove_container(container["uuid"])


def terminate_local_object(local_object):
    if is_local_object_an_app(local_object):
        # is an app
        containers = local_object.values()[0]["containers"]
        for container in containers:
            _terminate_local_container(container)
        return containers[0]["app_name"]
    else:
        # is a container
        _terminate_local_container(local_object)
        return local_object["uuid"]


def _logs_local_container(container):
    docker_client = get_docker_client()
    return docker_client.logs(container["uuid"])


def logs_local_object(local_object):
    if is_local_object_an_app(local_object):
        # is an app
        logs = ""
        containers = local_object.values()[0]["containers"]
        for container in containers:
            header = "======> %s <======" % container["name"]
            logs += header + "\n" + _logs_local_container(container) + "\n\n"
        return logs
    else:
        # is a container
        return _logs_local_container(local_object)


def details_local_object(local_object):
    if is_local_object_an_app(local_object):
        # is an app
        return local_object
    else:
        # is a container
        docker_client = get_docker_client()
        return docker_client.inspect_container(local_object["uuid"])


def is_local_object_an_app(local_object):
    return len(local_object) == 1


def get_port_list_from_string(ports_string):
    try:
        port_definitions = ports_string.split(",")
        port_list = []
        for port_definition in port_definitions:
            cleaned_port_definition = port_definition.replace(" ", "")
            port_and_protocol = cleaned_port_definition.split("->")[1].split("/")
            port_list.append({"inner_port": int(port_and_protocol[0]), "protocol": port_and_protocol[1]})
        return port_list
    except Exception:
        return []


def create_containers_for_an_app(image, tag, container_names, run_command, entrypoint, container_size="XS",
                                 ports={}, env_vars={}, already_deployed={}):
    docker_client = get_docker_client()
    deployed_ids = []
    try:
        pull_image(image, tag)
    except PublicImageNotFound:
        pass

    for i in range(len(container_names)):
        container_id = docker_client.create_container(image=":".join([image, tag]),
                                                      command=run_command, entrypoint=entrypoint,
                                                      ports=[(int(port["inner_port"]),
                                                              port["protocol"]) for port in ports],
                                                      environment=env_vars,
                                                      mem_limit=CONTAINER_SIZE[container_size]["memory"],
                                                      cpu_shares=CONTAINER_SIZE[container_size]["cpu_shares"],
                                                      name=container_names[i])
        docker_client.start(container_id["Id"],
                            links=already_deployed,
                            port_bindings=dict((int(port["inner_port"]), None) for port in ports))
        already_deployed[container_names[i]] = container_names[i] + "-link"
        deployed_ids.append(container_id["Id"])
    return deployed_ids


def pull_image(image, tag):
    docker_client = get_docker_client()
    result = docker_client.pull(image, tag)
    for line in result:
        if re.search("error", line) is not None or re.search("Error", line) is not None:
            raise PublicImageNotFound("Could not pull image %s:%s" % (image, tag))


def get_ports_from_image(image, tag):
    docker_client = get_docker_client()
    result = None
    try:
        pull_image(image, tag)
    except PublicImageNotFound as e:
        result = str(e)
    try:
        images = docker_client.images(name=image)
        return docker_client.inspect_image(
            get_image_id_from_imagelist(image, tag, images))["container_config"]["ExposedPorts"].keys()
    except Exception:
        raise Exception(result)


def get_image_id_from_imagelist(reponame, tag, image_list):
    for img in image_list:
        for repotag in img['RepoTags']:
            repo_tag = repotag.split(":")
            assert len(repo_tag) == 2, "Error when reading tags from %s" % repotag
            if repo_tag[0] == reponame and repo_tag[1] == tag:
                return img["Id"]
    raise Exception("Image %s:%s not in %s" % (reponame, tag, image_list))


def build_dockerfile(filepath, ports, command):
    with open(filepath, "w") as dockerfile:
        base_image = "FROM tutum/buildstep\n\n"
        expose_ports = " ".join(["EXPOSE", ports]) + "\n\n" if ports else ""
        if isinstance(command, list):
            command = ','.join(command)
            command = '[%s]' % command
        cmd = " ".join(["CMD", command])

        for line in [base_image, expose_ports, cmd]:
            if line:
                dockerfile.write(line)


def print_stream_line(line):
    dict_or_tuple = eval(line.replace("}{", "},{"))
    if isinstance(dict_or_tuple, dict):
        dict_or_tuple = (dict_or_tuple, )
    for message in dict_or_tuple:
        string = ""
        for key in message.keys():
            string += str(message[key]).replace("\n", "")
        print string.encode('utf8')


class JsonDatetimeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)

        return json.JSONEncoder.default(self, obj)
