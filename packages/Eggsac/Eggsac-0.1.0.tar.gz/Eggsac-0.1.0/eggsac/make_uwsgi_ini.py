#!/usr/bin/env python

"""
Create uWSGI and Nginx configuration for a Package in a virtualenv
"""

import os, sys
import argparse
import json
from collections import defaultdict

import utils

DESCRIPTION = "Create uWSGI and Nginx configuration for an Eggsac " \
              "in a virtualenv"
CONF_FORMAT = "{0}_nginx.conf"
INI_FORMAT  = "{0}_uwsgi.ini"

# Defaults
HTTP_PORT = 8000
SOCKET = "127.0.0.1:3031"
SERVER_NAME = "localhost"
PROCESSES = 4
THREADS = 10
STATS = "127.0.0.1:9191"
BUFFERSIZE = "32768"
NGINX_ACCESS_LOG = "/var/log/nginx/access.log"

def make_parser(
        parser=None,
        server_name=SERVER_NAME,
        http_port=HTTP_PORT,
        socket=SOCKET,
        processes=PROCESSES,
        threads=THREADS,
        stats=STATS,
        buffer_size=BUFFERSIZE,
        nginx_access_log=NGINX_ACCESS_LOG,
        nginx_add_headers='',
):
    if parser is None:
        parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.set_defaults(
        action='install',
    )

    parser.add_argument(
        'package', help='The Python package name; e.g., TodoCob')

    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '--install', dest='action', action='store_const', const='install',
        help='Install configuration')
    action_group.add_argument(
        '--remove', dest='action', action='store_const', const='remove',
        help='Remove configuration')

    parser.add_argument(
        '--virtualenv', '-V',
        help="Virtualenv that uWSGI must run the package in ['%(default)s']",
        default=os.getenv("VIRTUAL_ENV"))
    parser.add_argument(
        '--wsgi-file', '-W',
        help="Path to Python WSGI application",
        nargs=2, metavar=('PACKAGE', 'RELPATH'))
    parser.add_argument(
        '--build-version', '-B',
        help="Application build version")
    ini_action = parser.add_argument(
        '--ini', '-I',
        help="Name of target uWSGI ini file, [%(default)s]",
        default=INI_FORMAT.format("PACKAGE"))
    conf_action = parser.add_argument(
        '--conf', '-C',
        help="Name of target Nginx conf file, [%(default)s]",
        default=CONF_FORMAT.format("PACKAGE"))

    parser.add_argument(
        '--server-name', '-N',
        help="Server name that Nginx listens on, ['%(default)s']",
        default=server_name)
    parser.add_argument(
        '--http-port', '-P', type=int,
        help="HTTP port that Nginx listens on, [%(default)s]",
        default=http_port)
    parser.add_argument(
        '--socket', '-S',
        help="Socket shared by uWSGI and Nginx, ['%(default)s']",
        default=socket)
    parser.add_argument(
        '--processes', type=int,
        help="Number of worker processes used by uWSGI, [%(default)s]",
        default=processes)
    parser.add_argument(
        '--threads', type=int,
        help="Number of threads per worker proces used by uWSGI, "
             "[%(default)s]",
        default=threads)
    parser.add_argument(
        '--buffer-size', '-U', type=int,
        help="uWSGI internal buffer size of packet parsing, "
             "[%(default)s]",
        default=buffer_size)
    parser.add_argument(
        '--stats',
        help="Socket for uWSGI statistics, ['%(default)s']",
        default=stats)
    parser.add_argument(
        '--python-version',
        help="[%(default)s]",
        default=utils.PYTHON_VERSION)
    parser.add_argument(
        '--nginx-access-log',
        help="[%(default)s]",
        default=nginx_access_log)
    parser.add_argument(
        '--nginx-add-headers',
        help="[%(default)s]",
        default=nginx_add_headers)


    args = parser.parse_args()

    if args.conf == conf_action.default:
        args.conf = CONF_FORMAT.format(args.package.lower())
    if args.ini  == ini_action.default:
        args.ini  = INI_FORMAT.format(args.package.lower())

    return args, parser

def find_egg(args, package_name, relative=False):
    return utils.find_egg(
        args.virtualenv,
        package_name,
        relative=relative,
        python_version=args.python_version)

def validate(args, parser):
    if not args.virtualenv:
        if not "VIRTUAL_ENV" in os.environ:
            sys.stderr.write("Must be running in a virtualenv\n")
            parser.print_usage()
            sys.exit(1)
        else:
            args.virtualenv = os.environ["VIRTUAL_ENV"]

    args.wsgi_path = os.path.join(
        find_egg(args, args.wsgi_file[0]),
        args.wsgi_file[1])

    if not os.path.exists(args.wsgi_path):
        sys.stderr.write("{0} does not exist\n".format(args.wsgi_path))
        sys.exit(1)

    args.package_egg = find_egg(args, args.package)
    parse_add_headers(args, args.nginx_add_headers)

def parse_add_headers(args, add_headers):
    location_headers = parse_add_headers_parameter(add_headers)
    set_add_header(args, 'slash_add_headers', '/', location_headers)
    set_add_header(args, 'output_add_headers', '/output/', location_headers)
    return args

def parse_add_headers_parameter(add_headers):
    location_headers = defaultdict(list)
    if add_headers:
        for item in json.loads(add_headers):
            location_headers[item[0]].append(item[1])
    return location_headers

def set_add_header(args, attr, key, location_headers):
    value = location_headers.get(key, [])
    value = '\n'.join([("            add_header %s;" % v) for v in value])
    setattr(args, attr, value or '')

UWSGI_INI_TEMPLATE = """\
[uwsgi]
socket = {socket}
#http = :{http_port}
virtualenv = {virtualenv}
chdir = {package_egg}
wsgi-file = {wsgi_path}
processes = {processes}
threads = {threads}
stats = {stats}
master = true
plugins = python
buffer-size = {buffer_size}
"""

NGINX_CONF_TEMPLATE = """\
log_format cob '$remote_addr $http_x_forwarded_for $remote_user [$time_local] ($request_time) '
        '"$request" $status $body_bytes_sent '
        '"$http_referer" "$http_user_agent"';

server {{
        listen {http_port};
        server_name {server_name};

        location / {{
            uwsgi_pass {socket};
            include uwsgi_params;
            access_log {nginx_access_log} cob;
{slash_add_headers}
        }}

        # Static files
        location /output/ {{
            alias {package_egg}/output/;
            access_log {nginx_access_log} cob;
{output_add_headers}
        }}
}}
"""

def create_uwsgi_config(args, uwsgi_ini_template):
    with open(args.ini, "w") as f:
        f.write( uwsgi_ini_template.format(**args.__dict__) )

def create_nginx_config(args, nginx_conf_template):
    with open(args.conf, "w") as f:
        f.write( nginx_conf_template.format(**args.__dict__) )

def install_config(
        args,
        parser,
        uwsgi_ini_template=UWSGI_INI_TEMPLATE,
        nginx_conf_template=NGINX_CONF_TEMPLATE
):
    create_uwsgi_config(args, uwsgi_ini_template)
    create_nginx_config(args, nginx_conf_template)

def remove_config(args, parser):
    os.remove(args.ini)
    os.remove(args.conf)

def run(parser=None, **kwargs):
    args, parser = make_parser(parser, **kwargs)
    validate(args, parser)

    if args.action == 'install':
        install_config(args, parser)
    elif args.action == 'remove':
        remove_config(args, parser)
    else:
        raise ValueError("Unknown action: %s" % args.action)

    return args, parser


if __name__ == '__main__':
    run()
