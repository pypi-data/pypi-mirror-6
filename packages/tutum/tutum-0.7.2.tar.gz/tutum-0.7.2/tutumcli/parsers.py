import argparse


def add_login_parser(subparsers, parent_parser):
    subparsers.add_parser('login', help='Login into Tutum', description='Login into Tutum', parents=[parent_parser])


def add_apps_parser(subparsers, parent_parser):
    apps_parser = subparsers.add_parser('apps', help='List running applications',
                                        description='List running applications',
                                        parents=[parent_parser])
    apps_parser.add_argument("-q", "--quiet", help="Print only long uuids", action='store_true')
    apps_parser.add_argument("-s", "--status", help="Filter applications by status")

    # App common options
    app_common_parser = argparse.ArgumentParser(add_help=False)
    app_common_parser.add_argument("identifier", help="Application's uuid (either long or short) or name", nargs="+")

    create_app_parser = subparsers.add_parser('run', help='Create and run an application',
                                              description='Create and run an application', parents=[parent_parser])
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

    subparsers.add_parser('inspect', help='Inspect an application', description='Inspect an application',
                          parents=[parent_parser, app_common_parser])
    subparsers.add_parser('start', help='Start an application', description='Start an application',
                                             parents=[parent_parser, app_common_parser])
    subparsers.add_parser('stop', help='Stop an application', description='Stop an application', parents=[parent_parser, app_common_parser])
    subparsers.add_parser('terminate', help='Terminate an application', description='Terminate an application',
                          parents=[parent_parser, app_common_parser])
    subparsers.add_parser('logs', help='Get logs from an application', description='Get logs from an application',
                          parents=[parent_parser, app_common_parser])
    scale_app_parser = subparsers.add_parser('scale', help='Scale an application',
                                             description='Scale an application',
                                             parents=[parent_parser, app_common_parser])
    scale_app_parser.add_argument("target_num_containers",
                                  help="target number of containers to scale this application to",
                                  type=int)

    alias_app_parser = subparsers.add_parser('alias', help="Change application's dns",
                                             description="Change application's dns",
                                             parents=[parent_parser, app_common_parser])
    alias_app_parser.add_argument("dns", help="custom domain to use for this web application")


def add_containers_parser(subparsers, parent_parser):
    containers_parser = subparsers.add_parser('ps', help='List running containers',
                                              description='List running containers', parents=[parent_parser])
    containers_parser.add_argument("-i", "--identifier", help="Application's uuid (either long or short) or name")
    containers_parser.add_argument("-q", "--quiet", help="Print only long uuids", action='store_true')
    containers_parser.add_argument("-s", "--status", help="Filter containers by status")

    # Container common options
    container_common_parser = argparse.ArgumentParser(add_help=False)
    container_common_parser.add_argument("identifier", help="Container's uuid (either long or short) or name", nargs="+")

    subparsers.add_parser('inspect-container', help='Inspect a container', description='Inspect a container',
                          parents=[parent_parser, container_common_parser])
    subparsers.add_parser('start-container', help='Start a container', description='Start a container',
                          parents=[parent_parser,  container_common_parser])
    subparsers.add_parser('stop-container', help='Stop a container', description='Stop a container',
                          parents=[parent_parser, container_common_parser])
    subparsers.add_parser('terminate-container', help='Terminate a container', description='Terminate a container',
                          parents=[parent_parser, container_common_parser])
    subparsers.add_parser('logs-container', help='Get logs from a container', description='Get logs from a container',
                          parents=[parent_parser, container_common_parser])


def add_images_parser(subparsers, parent_parser):
    images_parser = subparsers.add_parser('images', help='List private images', description='List private images',
                                          parents=[parent_parser])
    images_parser.add_argument("-q", "--quiet", help="Print only image names", action='store_true')
    image_list_options = images_parser.add_mutually_exclusive_group()
    image_list_options.add_argument("-j", "--jumpstarts", help="List jumpstart images", action='store_true')
    image_list_options.add_argument("-l", "--linux", help="List linux images", action='store_true')

    add_new_image_parser = subparsers.add_parser('add', help='Add a private image', description='Add a private image',
                                                 parents=[parent_parser])
    add_new_image_parser.add_argument("repository", help="Full image repository, i.e. quay.io/tutum/test-repo")
    add_new_image_parser.add_argument("username", help="Username to authenticate with the registry")
    add_new_image_parser.add_argument("password", help="Username password")
    add_new_image_parser.add_argument("-d", "--description", help="Image description")

    # image common options
    image_common_parser = argparse.ArgumentParser(add_help=False)
    image_common_parser.add_argument("repository", help="Full image repository, i.e. quay.io/tutum/test-repo", nargs="+")

    subparsers.add_parser('remove', help='Remove a private image', description='Remove a private image',
                          parents=[parent_parser, image_common_parser])

    update_image_parser = subparsers.add_parser('update', help='Update a private image',
                                                description='Update a private image',
                                                parents=[parent_parser, image_common_parser])
    update_image_parser.add_argument("-u", "--username", help="New username to authenticate with the registry")
    update_image_parser.add_argument("-p", "--password", help="New username password")
    update_image_parser.add_argument("-d", "--description", help="New image description")