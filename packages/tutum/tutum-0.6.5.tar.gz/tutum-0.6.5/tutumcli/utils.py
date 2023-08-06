from tabulate import tabulate
import datetime
import re
import tutum

from tutumcli.exceptions import NonUniqueIdentifier, ObjectNotFound


def tabulate_result(data_list, headers):
    print tabulate(data_list, headers, stralign="left")


def humanize_date_difference_from_now(target_datetime):
    now = datetime.datetime.utcnow()
    dt = target_datetime - datetime.datetime.utcnow()
    offset = dt.seconds + (dt.days * 60*60*24)
    delta_s = offset % 60
    offset /= 60
    delta_m = offset % 60
    offset /= 60
    delta_h = offset % 24
    offset /= 24
    delta_d = offset

    if delta_d > 1:
        if delta_d > 6:
            date = now + datetime.timedelta(days=-delta_d, hours=-delta_h, minutes=-delta_m)
            return date.strftime('%A, %Y %B %m, %H:%I')
        else:
            wday = now + datetime.timedelta(days=-delta_d)
            return wday.strftime('%A')
    if delta_d == 1:
        return "Yesterday"
    if delta_h > 0:
        return "%dh%dm ago" % (delta_h, delta_m)
    if delta_m > 0:
        return "%dm%ds ago" % (delta_m, delta_s)
    else:
        return "%ds ago" % delta_s


def is_uuid4(identifier):
    uuid4_regexp = re.compile('^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}', re.I)
    match = uuid4_regexp.match(identifier)
    return bool(match)


def fetch_container(identifier):

    if is_uuid4(identifier):
        return tutum.Container.fetch(identifier)
    else:
        objects_same_identifier = tutum.Container.list(unique_name=identifier) or \
                                  tutum.Container.list(uuid__startswith=identifier)
        if len(objects_same_identifier) == 1:
            return objects_same_identifier[0]
        elif len(objects_same_identifier) == 0:
            raise ObjectNotFound("Cannot find a container with the identifier '%s'" % identifier)
        raise NonUniqueIdentifier("More than one container has the same identifier, please use the long uuid")


def fetch_app(identifier):

    if is_uuid4(identifier):
        return tutum.Application.fetch(identifier)
    else:
        objects_same_identifier = tutum.Application.list(name=identifier) or \
                                  tutum.Application.list(uuid__startswith=identifier)
        if len(objects_same_identifier) == 1:
            return objects_same_identifier[0]
        elif len(objects_same_identifier) == 0:
            raise ObjectNotFound("Cannot find an application with the identifier '%s'" % identifier)
        raise NonUniqueIdentifier("More than one application has the same identifier, please use the long uuid")
