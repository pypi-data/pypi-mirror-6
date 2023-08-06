import datetime
import re
import multiprocessing

from tabulate import tabulate
import tutum
from dateutil import tz
import ago

from tutumcli.exceptions import NonUniqueIdentifier, ObjectNotFound, BadParameter


def tabulate_result(data_list, headers):
    print tabulate(data_list, headers, stralign="left", tablefmt="plain")


def _from_utc_string_to_utc_datetime(utc_datetime_string):
    if not utc_datetime_string:
        return None
    utc_date_object = datetime.datetime.strptime(utc_datetime_string, "%a, %d %b %Y %H:%M:%S +0000")

    return utc_date_object


def get_humanize_local_datetime_from_utc_datetime_string(utc_datetime_string):
    local_now = datetime.datetime.now(tz.tzlocal())
    utc_target_datetime = _from_utc_string_to_utc_datetime(utc_datetime_string)
    if utc_target_datetime:
        local_target_datetime = _from_utc_string_to_utc_datetime(utc_datetime_string).replace(tzinfo=tz.gettz("UTC")).astimezone(tz=tz.tzlocal())
        return ago.human(local_now - local_target_datetime, precision=1)
    return ""


def is_uuid4(identifier):
    uuid4_regexp = re.compile('^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}', re.I)
    match = uuid4_regexp.match(identifier)
    return bool(match)


def fetch_container(identifier, raise_exceptions=True):

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


def fetch_app(identifier, raise_exceptions=True):

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


def parse_ports(port_list):
    if port_list is not None:
        parsed_ports = []
        for port in port_list:
            parsed_ports.append(_get_port_dict(port))
    else:
        parsed_ports = None
    return parsed_ports


def _get_port_dict(port):
    port_regexp = re.compile('^[0-9]{1,5}/(tcp|udp)$', re.I)
    match = port_regexp.match(port)
    if bool(match):
        port = port.split("/", 1)
        inner_port = int(port[0])
        protocol = port[1].lower()
        return {'protocol': protocol, 'inner_port': inner_port}
    raise BadParameter("Port argument %s does not match with 'port/protocol'. Example: 80/tcp" % port)


def parse_envvars(envvar_list):
    if envvar_list is not None:
        parsed_envvars = []
        for envvar in envvar_list:
            parsed_envvars.append(_is_envvar(envvar))
    else:
        parsed_envvars = None
    return parsed_envvars


def _is_envvar(envvar):
    envvar_regexp = re.compile('^[a-zA-Z_]+[a-zA-Z0-9_]*=[^?!=]+$', re.I)
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
    apps_result = pool.apply_async(fetch_app, (identifier, False, ))
    containers_result = pool.apply_async(fetch_container, (identifier, False, ))
    pool.close()
    pool.join()

    app = apps_result.get()
    container = containers_result.get()

    if isinstance(app, ObjectNotFound) and isinstance(container, ObjectNotFound):
        raise ObjectNotFound("Cannot find an application or a container with identifier '%s'" % identifier)
    elif isinstance(app, NonUniqueIdentifier) or isinstance(container, NonUniqueIdentifier):
        raise NonUniqueIdentifier("Identifier '%s' is being used by more than one container and/or application, "
                                  "please use the long uuid" % identifier)
    elif not isinstance(app, ObjectNotFound):
        return app

    elif not isinstance(container, ObjectNotFound):
        return container

    return None
