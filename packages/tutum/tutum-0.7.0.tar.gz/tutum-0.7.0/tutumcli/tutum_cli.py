import argparse
import logging

from tutumcli import parsers
from tutumcli import commands


VERSION = "0.7.0"


logging.basicConfig()

# Main parser
parser = argparse.ArgumentParser(description="Tutum's CLI", prog="tutum")
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)

subparsers = parser.add_subparsers(title="Tutum's CLI commands", dest='command')

# Common options
parent_parser = argparse.ArgumentParser(add_help=False)

# Commands
parsers.add_login_parser(subparsers, parent_parser)
parsers.add_apps_parser(subparsers, parent_parser)
parsers.add_containers_parser(subparsers, parent_parser)


def main():
    # Parse args
    args = parser.parse_args()
    if args.command == "login":
        commands.authenticate()
    elif args.command == "apps":
        commands.apps(args.quiet, args.all)
    elif args.command == "inspect":
        commands.application_details(args.identifier)
    elif args.command == "start":
        commands.app_start(args.identifier)
    elif args.command == "stop":
        commands.app_stop(args.identifier)
    elif args.command == "terminate":
        commands.app_terminate(args.identifier)
    elif args.command == "logs":
        commands.app_logs(args.identifier)
    elif args.command == "scale":
        commands.app_scale(args.identifier, args.target_num_containers)
    elif args.command == "alias":
        commands.app_alias(args.identifier, args.dns)
    elif args.command == "run":
        commands.app_run(image=args.image, name=args.name, container_size=args.container_size,
                         target_num_containers=args.target_num_containers, run_command=args.run_command,
                         entrypoint=args.entrypoint, container_ports=args.port,
                         container_envvars=args.env,
                         linked_to_application=args.link, autorestart=args.autorestart,
                         autoreplace=args.autoreplace, autodestroy=args.autodestroy, roles=args.role)
    elif args.command == "ps":
            commands.ps(args.identifier, args.quiet, args.all)
    elif args.command == "inspect-container":
        commands.container_inspect(args.identifier)
    elif args.command == "logs-container":
        commands.container_logs(args.identifier)
    elif args.command == "start-container":
        commands.container_start(args.identifier)
    elif args.command == "stop-container":
        commands.container_stop(args.identifier)
    elif args.command == "terminate-container":
        commands.container_terminate(args.identifier)

if __name__ == "__main__":
    main()