import argparse


def add_login_parser(subparsers, parent_parser):
    login_parser = subparsers.add_parser('login', help='Login into Tutum', parents=[parent_parser])
    return login_parser


def add_apps_parser(subparsers, parent_parser):
    apps_parser = subparsers.add_parser('apps', help='List running applications', parents=[parent_parser])
    apps_parser.add_argument("-q", "--quiet", help="Print only long uuids", action='store_true')
    apps_parser.add_argument("-a", "--all", help="List all applications", action='store_true')

    # App common options
    app_common_parser = argparse.ArgumentParser(add_help=False)
    app_common_parser.add_argument("identifier", help="Application's uuid (either long or short) or name", nargs="+")

    create_app_parser = subparsers.add_parser('run', help='Create and run an application', parents=[parent_parser])
    create_app_parser.add_argument("image", help="the image used to deploy this application in docker format")
    create_app_parser.add_argument("-n", "--name", help="a human-readable name for the application "
                                                        "(default: image_tag without namespace)")
    create_app_parser.add_argument("-s", "--container_size", help="the size of the application containers "
                                                                  "(default: XS, possible values: XS, S, M, L, XL)")
    create_app_parser.add_argument("-t", "--target_num_containers", help="the number of containers to run "
                                                                         "for this application (default: 1)", type=int)
    create_app_parser.add_argument("-r", "--run_command",
                                   help="the command used to start the application containers "
                                        "(default: as defined in the image)")
    create_app_parser.add_argument("--entrypoint",
                                   help="the command prefix used to start the application containers "
                                        "(default: as defined in the image)")
    create_app_parser.add_argument("-p", "--port",
                                   help="set ports i.e. '80/tcp'"
                                        "(default: as defined in the image)", action='append')
    create_app_parser.add_argument("-e", "--env",
                                   help="set environment variables i.e. 'ENVVAR=foo' "
                                        "(default: as defined in the image, plus any link- or role-generated variables)",
                                   action='append')
    create_app_parser.add_argument("-l", "--link",
                                   help="an application's uuid (either long or short) or name to link this application "
                                        "to, i.e. 80ff1635-2d56-478d-a97f-9b59c720e513'] (default: none)",
                                   action='append')
    create_app_parser.add_argument('--autorestart', help="whether the containers should be restarted if they stop "
                                                         "(default: OFF)", choices=['OFF', 'ON_FAILURE', 'ALWAYS'])
    create_app_parser.add_argument('--autoreplace', help="whether the containers should be replaced with a new one if "
                                                         "they stop (default: OFF)",
                                   choices=['OFF', 'ON_FAILURE', 'ALWAYS'])
    create_app_parser.add_argument('--autodestroy', help="whether the containers should be terminated if "
                                                         "they stop (default: OFF)",
                                   choices=['OFF', 'ON_FAILURE', 'ALWAYS'])
    create_app_parser.add_argument('--role', help="Tutum API roles to grant the application, "
                                                  "i.e. 'global' (default: none, possible values: 'global')",
                                   action='append')

    inspect_app_parser = subparsers.add_parser('inspect', help='Inspect an application',
                                               parents=[parent_parser, app_common_parser])
    start_app_parser = subparsers.add_parser('start', help='Start an application',
                                             parents=[parent_parser, app_common_parser])
    stop_app_parser = subparsers.add_parser('stop', help='Stop an application',
                                            parents=[parent_parser, app_common_parser])
    terminate_app_parser = subparsers.add_parser('terminate', help='Terminate an application',
                                                 parents=[parent_parser, app_common_parser])
    logs_app_parser = subparsers.add_parser('logs', help='Get logs from an application',
                                            parents=[parent_parser, app_common_parser])
    scale_app_parser = subparsers.add_parser('scale', help='Scale an application',
                                             parents=[parent_parser, app_common_parser])
    scale_app_parser.add_argument("target_num_containers",
                                  help="target number of containers to scale this application to",
                                  type=int)

    alias_app_parser = subparsers.add_parser('alias', help="Change application's dns",
                                             parents=[parent_parser, app_common_parser])
    alias_app_parser.add_argument("dns", help="custom domain to use for this web application")

    return apps_parser


def add_containers_parser(subparsers, parent_parser):
    containers_parser = subparsers.add_parser('ps', help='List running containers', parents=[parent_parser])
    containers_parser.add_argument("-i", "--identifier", help="Application's uuid (either long or short) or name")
    containers_parser.add_argument("-q", "--quiet", help="Print only long uuids", action='store_true')
    containers_parser.add_argument("-a", "--all", help="List all containers", action='store_true')

    # Container common options
    container_common_parser = argparse.ArgumentParser(add_help=False)
    container_common_parser.add_argument("identifier", help="Container's uuid (either long or short) or name", nargs="+")

    inspect_container_parser = subparsers.add_parser('inspect-container', help='Inspect a container',
                                                     parents=[parent_parser, container_common_parser])
    start_container_parser = subparsers.add_parser('start-container', help='Start a container',
                                                   parents=[parent_parser, container_common_parser])
    stop_container_parser = subparsers.add_parser('stop-container', help='Stop a container',
                                                  parents=[parent_parser, container_common_parser])
    terminate_container_parser = subparsers.add_parser('terminate-container', help='Terminate a container',
                                                       parents=[parent_parser, container_common_parser])
    logs_container_parser = subparsers.add_parser('logs-container', help='Get logs from a container',
                                                  parents=[parent_parser, container_common_parser])

    return containers_parser
