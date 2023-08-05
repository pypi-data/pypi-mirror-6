# -*- coding: utf-8 -*-

"""Create a deployable package from a Cob."""

# Prerequisites:
#  Python packages: virtualenv, argparse
# Optional:
#  Ruby Gems: fpm

from __future__ import absolute_import

import argparse
import datetime
import json
import os
import shlex
import shutil
import sys
import tempfile
import virtualenv

try:
    import eggsac.utils as utils
    import eggsac.debian as debian
except ImportError:
    import utils
    import debian


def parse_args(**kwargs):
    parser = argparse.ArgumentParser(
        description='Create a deployable virtualenv for an application')

    parser.set_defaults(
        rpm=None,
        squash_fs=None,
        wheel=None,
        configure_uwsgi=os.path.join("bin", "configure_uwsgi"),
        nginx_add_headers='',
        tmp_dir=tempfile.gettempdir(), 
    )

    parser.add_argument(
        'package_path', metavar='APP_PACKAGE_DIR',
        help='directory where Python application lives '
             '(default: %(default)s)',
        default=kwargs.get('package_path', '.'), nargs='?')

    parser.add_argument(
        '--local-package', '-L', dest='local_packages',
        action='append', metavar='PACKAGE_DIR',
        help='Local Packages to be installed before APP_PACKAGE_DIR '
             '(default: %(default)s)',
        default=kwargs.get('local_packages', []))

    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        '--verbose', '-v', action='count', default=0,
        help='Verbose mode. Can be supplied multiple times '
             'to increase verbosity.')
    verbosity_group.add_argument(
        '--quiet', '-q', action='count', default=0,
        help='Decrease verbosity')

    filename_group = parser.add_argument_group(
        title="Filename Options",
        description="Components of package filename")
    filename_group.add_argument(
        '--root-prefix', default=kwargs.get('root_prefix', ''),
        help='Prefix to root of virtualenv (default: "%(default)s")')
    filename_group.add_argument(
        '--python-package', '-P', default=kwargs.get('python_package'),
        help='Python package name (default: %(default)s)')
    filename_group.add_argument(
        '--package-version', '-V', default=kwargs.get('package_version'),
        help='Python package version (default: %(default)s)')
    filename_group.add_argument(
        '--tmp-dir',
        help='Temp directory where all output is compiled '
             '(default: "%(default)s")')
    filename_group.add_argument(
        '--version-format', '-F',
        default=kwargs.get(
            'package_version',
            '%(package_version)s-%(build_date)s-%(branch_name)s-%(sha)s'),
        help='version format string (default: "%(default)s")')
    filename_group.add_argument(
        '--build-date',
        help='Build date (default: computed)')
    filename_group.add_argument(
        '--branch-name',
        help='Git/Mercurial branch name (default: computed)')
    filename_group.add_argument(
        '--build-number', type=int, default=0,
        help='Build number (e.g., from Jenkins) (default: %(default)s)')

    package_group = parser.add_argument_group(
        title="Package Options",
        description="Type of package(s) to generate")

    debian_group = package_group.add_mutually_exclusive_group()
    debian_group.add_argument(
        '--deb', '-D', action='store_true',
        help='Create a Debian package')
    debian_group.add_argument(
        '--no-deb', dest='deb', action='store_false',
        help='Do not create a Debian package')

#   package_group.add_argument(
#       '--rpm', '-R', action='store_true',
#       help='Create an RPM package (not yet implemented)')

#   package_group.add_argument(
#       '--squash-fs', '--sqsh', '-S', action='store_true',
#       help='Create a SquashFS squashed file system (not yet implemented)')

    tar_gzip_group = package_group.add_mutually_exclusive_group()
    tar_gzip_group.add_argument(
        '--tar-gzip', '--tgz', '-T', action='store_true',
        help='Create a Gzipped Tarfile')
    tar_gzip_group.add_argument(
        '--no-tar-gzip', dest='tar_gzip', action='store_false',
        help='Do not create a Gzipped Tarfile')

#   package_group.add_argument(
#       '--wheel', '-W', action='store_true',
#       help='Create a Python Wheel (not yet implemented)')

    zip_group = package_group.add_mutually_exclusive_group()
    zip_group.add_argument(
        '--zip', '-Z', action='store_true',
        help='Create a Zipfile')
    zip_group.add_argument(
        '--no-zip', dest='zip', action='store_false',
        help='Do not create a Zipfile')

    delete_virtualenv_group = parser.add_mutually_exclusive_group()
    delete_virtualenv_group.add_argument(
        '--delete-virtualenv', dest='delete_virtualenv',
        action='store_true', default=True,
        help='Delete created virtualenv when finished (default: %(default)s)')
    delete_virtualenv_group.add_argument(
        '--keep-virtualenv', '-K', dest='delete_virtualenv', action='store_false',
        help='Keep created virtualenv when finished')

    additional_group = parser.add_argument_group(
        title="Additional Options")

    additional_group.add_argument(
        '--output-dir', '-o',
        help='Output packages will be copied here')
    additional_group.add_argument(
        '--index-url', '-i',
        help='Base URL of Python Package Index')
    additional_group.add_argument(
        '--dry-run', '-n', action='store_true', default=False,
        help='Show what would be generated.')
    additional_group.add_argument(
        '--config-filename', default=kwargs.get('config_filename'),
        help='Config filename (default: %(default)s)')
    additional_group.add_argument(
        '--always-unzip', default=kwargs.get('always_unzip', []), nargs='*',
        help='Python package dependencies that must be built with '
             '--always-unzip')

    uwsgi_group = additional_group.add_mutually_exclusive_group()
    uwsgi_group.add_argument(
        '--uwsgi', '-U', default=False, action='store_true',
        help='Generate uwsgi.ini and nginx.conf wrappers '
             '(default: %(default)s)')
    uwsgi_group.add_argument(
        '--no-uwsgi', dest='uwsgi', action='store_false',
        help='Do not generate uwsgi.ini and nginx.conf wrappers')

    additional_group.add_argument(
        '--uwsgi-configure',
        help="Path to install-time uWSGI init, (default: %(default)s)",
        nargs=2, metavar=('PACKAGE', 'RELPATH'),
        default=kwargs.get('uwsgi_configure'))

    additional_group.add_argument(
        '--wsgi-file',
        help="Path to runtime Python WSGI application, (default: %(default)s)",
        nargs=2, metavar=('PACKAGE', 'RELPATH'),
        default=kwargs.get('wsgi_file'))

    additional_group.add_argument(
        '--fpm-path', default='fpm',
        help='Path to FPM tool; '
             'e.g., "fpm" or "rvm <RUBY_VER>@<GEMSET> do fpm" '
             '(default: %(default)s)')

    return parser.parse_args()

def make_logger(args):
    verbosity = args.verbose - args.quiet
    # Use same logger when invoking virtualenv code
    args.logger = virtualenv.logger = virtualenv.Logger(
        [(virtualenv.Logger.level_for_integer(2 - verbosity), sys.stdout)])

def find_package_dir(args):
    args.package_path = utils.abspath(args.package_path)
    args.vcs = utils.find_vcs(args.package_path)
    # TODO: raise if args.vcs is None?

def read_args_ini_config(args):
    args.ini_config = utils.read_ini(
        args.package_path, args.config_filename)

    if args.ini_config.has_option('setup', 'always_unzip'):
        args.always_unzip = args.always_unzip or []
        args.always_unzip.extend(
            utils.read_list(
                args.ini_config, 'setup', 'always_unzip'))

    if args.ini_config.has_option('setup', 'wsgi_file'):
        args.wsgi_file = utils.read_list(
            args.ini_config, 'setup', 'wsgi_file')
    if args.ini_config.has_section('setup.nginx.add_header'):
        args.nginx_add_headers = args.ini_config.items('setup.nginx.add_header')

def find_python_package(args):
    read_args_ini_config(args)
    for a,k in [
            ('python_package',  'package_name'),
            ('package_version', 'version'),
            ('index_url',       'index_url'),
    ]:
        attr = getattr(args, a)
        if not attr and args.ini_config.has_option('setup', k):
            attr = args.ini_config.get('setup', k)
        if attr:
            setattr(args, a,  attr)

def now(args):
    return datetime.datetime.now() # TODO: utcnow?

def elapsed_time(args, then=None):
    return (now(args) - (then or args.start_time)).total_seconds()

def compute_build_time(args):
    args.build_time = args.start_time = now(args)
    args.build_time_str = args.build_time.strftime("%Y%m%dt%H%M")

def compute_package_name(args):
    args.debian_pkgname = args.python_package.lower()
    args.debian_pkgvername = args.debian_pkgname #+ "-" + args.package_version
    args.build_version = compute_build_version(args)
    args.package_name   = (
        args.python_package
#       + "-" + args.package_version
        + "_" + args.build_version)

def compute_build_version(args):
    version_data = dict(
        package_version=args.package_version,
        build_date=args.build_date or args.build_time_str,
        branch_name=args.branch_name or args.vcs.current_branch(),
        build_number=args.build_number,
        sha=args.vcs.sha(),
        revision=args.vcs.revision(),
    )
    return args.version_format % version_data

def verify_root_prefix(args):
    if args.root_prefix:
        if os.path.isabs(args.root_prefix):
            raise ValueError("--root-prefix must not be absolute")
    elif args.root_prefix != '':
        raise ValueError("When empty, --root-prefix must be ''")

def compute_virtualenv_path(args):
    verify_root_prefix(args)
    args.root_dir = utils.abspath(
        os.path.join(args.tmp_dir, args.package_name))
    args.virtualenv_path = os.path.join(
        args.root_dir, args.debian_pkgvername)
    args.virtualenv_python_exe = utils.virtualenv_python_exe(
        args.virtualenv_path)

def initialize_args(args):
    make_logger(args)
    compute_build_time(args)
    find_package_dir(args)
    find_python_package(args)
    compute_package_name(args)
    compute_virtualenv_path(args)
    getattr(args.logger, "notify" if args.dry_run else "debug")(
        "%r" % args)
    return args

def create_readme(args):
    banner = """\
This virtualenv was created on %(start_time)s by
'%(argv)r'

Run 'source bin/activate' to use it.
""" % dict(
    start_time = args.start_time,
    argv = sys.argv,
    )
    args.logger.info(banner)
    if not args.dry_run:
        with open(os.path.join(args.virtualenv_path, "README"), "w") as f:
            f.write(banner)
            # TODO? Append cob's README

def virtualenv_byte_compile_lib(args):
    """Byte-compile lib/pythonN.N/*.py. Otherwise, some of them may be
    compiled at run time. These files will be left behind when the
    virtualenv is uninstalled."""
    if not args.dry_run:
        lib_dir = os.path.join(
            args.virtualenv_path, "lib", "python" + utils.PYTHON_VERSION)
        filter = lambda ext: set(os.path.splitext(f)[0]
                                 for f in os.listdir(lib_dir) if f.endswith(ext))
        uncompiled_files = filter('.py') - filter('.pyc')
        if uncompiled_files:
            run_virtualenv_command(["-c", "import " + ", ".join(uncompiled_files)], args)

def make_virtualenv(args):
    args.logger.info("Making virtualenv '%s'" % args.virtualenv_path)
    if not args.dry_run:
        utils.create_virtualenv(args.virtualenv_path)
    create_readme(args)
    virtualenv_byte_compile_lib(args)

def run_virtualenv_command(params, args, command=None, *pargs, **kwargs):
    popenargs = [command or args.virtualenv_python_exe] + params
    args.logger.info("Running %r in %r" % (popenargs, kwargs.get('cwd', '.')))
    if not args.dry_run:
        result = utils.run_command(
            popenargs,
            env=utils.fake_virtualenv(args.virtualenv_path),
            logger=args.logger,
            *pargs, **kwargs)
        args.logger.info('\n'.join(result))
        return result

def setup_cfg_context_manager(args, dir):
    return utils.setup_cfg_context_manager(
        not args.dry_run and args.index_url, dir)

def popen_verbose(args):
    return ["-v"] if args.verbose else []

def popen_index_url(args):
    return ["-i", utils.urlify(args.index_url)] if args.index_url else []

def virtualenv_setup_command(args, verb, cwd, *pargs, **kwargs):
    with setup_cfg_context_manager(args, cwd):
        run_virtualenv_command(
            ["setup.py"] + popen_verbose(args) + [verb],
            args, cwd=cwd, *pargs, **kwargs)

def virtualenv_pip_command(args, verb, pip_args=None, *pargs, **kwargs):
    params = [verb] + popen_verbose(args) + (pip_args or [])
    run_virtualenv_command(params, args, command="pip", *pargs, **kwargs)

def virtualenv_pip_install(args, packages, *pargs, **kwargs):
    virtualenv_pip_command(
        args,
        "install",
        pip_args=popen_index_url(args) + packages,
        *pargs, **kwargs)

def install_always_unzips_in_virtualenv(args, *pargs, **kwargs):
    if args.always_unzip:
        args.logger.notify("Installing %r in virtualenv as unzipped eggs",
                           args.always_unzip)
        with setup_cfg_context_manager(args, args.package_path):
            for uz in args.always_unzip:
                run_virtualenv_command(
                    ["--always-unzip"] + popen_verbose(args) + [uz],
                    args, command="easy_install",
                    cwd=args.package_path, *pargs, **kwargs)

def install_package_in_virtualenv(dir, args, *pargs, **kwargs):
    args.logger.notify("Installing '%s' in virtualenv", dir)
    virtualenv_setup_command(args, "install", cwd=dir, *pargs, **kwargs)

def install_all_packages_in_virtualenv(args, *pargs, **kwargs):
    for lp in args.local_packages:
        install_package_in_virtualenv(lp, args, *pargs, **kwargs)
    install_package_in_virtualenv(args.package_path, args, *pargs, **kwargs)

def relocate_virtualenv(args):
    args.logger.notify("Relocating virtualenv")
    try:
        # Virtualenv is too noisy
        notify, warn = virtualenv.logger.notify, virtualenv.logger.warn
        virtualenv.logger.notify = virtualenv.logger.warn = virtualenv.logger.info
        if not args.dry_run:
            utils.cleanup_virtualenv(args.virtualenv_path)
            virtualenv.make_environment_relocatable(args.virtualenv_path)
    finally:
        virtualenv.logger.notify, virtualenv.logger.warn = notify, warn

    if not args.dry_run:
        utils.make_activate_relative(args.virtualenv_path)


ConfigureUWsgiTemplate = """\
#!/bin/bash

if [ "$(whoami)" != "root" ]; then
    echo "You must run this script as an elevated user. Try running this script again as 'sudo ${{0}}'"
    exit 1
fi

VIRTUAL_ENV="$(cd $(dirname "$0")/..; pwd)"
UWSGI_CONFIGURE="$VIRTUAL_ENV/{uwsgi_configure}"
UWSGI_INI="{uwsgi_ini}"
NGINX_CONF="{nginx_conf}"

service nginx stop
service uwsgi stop

case "$1" in
    install)
        FLAG=--install
    ;;

    remove)
        FLAG=--remove
    ;;

    *)
        echo "Argument should be 'install' or 'remove'"
    ;;
esac

shift
source "$VIRTUAL_ENV/bin/activate"
python "$UWSGI_CONFIGURE" \\
    "$FLAG" \\
    --ini "$UWSGI_INI" \\
    --conf "$NGINX_CONF" \\
    --wsgi-file {wsgi_file} \\
    --build-version {build_version} \\
    --nginx-add-headers='{nginx_add_headers}' \\
    "{python_package}" $*

service uwsgi start
service nginx start
"""

def generate_uwsgi_config(args):
    args.logger.info("Generating UWSGI config")
    # We don't know the absolute path of the virtualenv on the
    # deployment machine, so we invoke this script on that machine
    # to generate uwsgi.ini and nginx.conf
    script_filename = os.path.join(args.virtualenv_path, args.configure_uwsgi)
    if args.dry_run:
        uwsgi_configure = "bin/example_uwsgi_configure.py"
    else:
        uwsgi_configure = os.path.join(
            utils.find_egg(
                args.virtualenv_path,
                args.uwsgi_configure[0],
                relative=True),
            args.uwsgi_configure[1])
    pkg_lower = args.python_package.lower()
    template_args = dict(
        uwsgi_configure = uwsgi_configure,
        python_package = args.python_package,
        build_version = args.build_version,
        uwsgi_ini  = "/etc/uwsgi/apps-enabled/{0}.ini".format(pkg_lower),
        nginx_conf = "/etc/nginx/sites-enabled/{0}.conf".format(pkg_lower),
        wsgi_file = ' '.join(args.wsgi_file),
        nginx_add_headers = json.dumps(args.nginx_add_headers),
    )

    script = ConfigureUWsgiTemplate.format(**template_args)

    args.logger.notify("Pregenerating uWSGI and Nginx config in virtualenv")
    if args.dry_run:
        args.logger.notify(script)
    else:
        with open(script_filename, "w") as f:
            f.write(script)
        os.chmod(script_filename, 0755)

def generate_additional_config(args):
    args.logger.notify("Generating additional config")
    if args.uwsgi:
        generate_uwsgi_config(args)


def fpm_package(args, output_type, package_name=None):
    cwd = utils.abspath(os.path.join(args.virtualenv_path, ".."))
    srcdir = args.package_name
    package_name = package_name or args.package_name
    outfile = os.path.join(cwd, package_name + "." + output_type)
    popenargs = shlex.split(args.fpm_path) + [
                 "-n", package_name,
                 '-s', 'dir',
                 '-t', output_type,
                 srcdir]
    args.logger.info("Running %r in %r" % (popenargs, cwd))
    result = []
    if not args.dry_run:
        result = utils.run_command(popenargs, cwd=cwd, logger=args.logger)
        args.logger.info('\n'.join(result))
    return (outfile, result)

def move_output(args, output_filename, target_basename=None):
    if args.output_dir:
        args.logger.info("Moving %s to %s/%s" % (
            output_filename, args.output_dir, target_basename or ''))
        if not args.dry_run:
            utils.move_file_to_dir(
                output_filename, args.output_dir, target_basename)

def package_virtualenv_debian(args):
    args.logger.info("Creating Debian package")
    package_vars = dict(
        package = args.debian_pkgname,
        root_prefix = args.root_prefix,
        full_version = args.build_version,
#       maintainer = "???", # FIXME
        description = args.python_package, # FIXME
    )
    if args.uwsgi:
        configure_uwsgi = os.path.join(
            "/" + args.root_prefix + args.debian_pkgname,
            args.configure_uwsgi)
        package_vars['depends'] = [
            'uwsgi', 'uwsgi-plugin-python', 'nginx']
        package_vars['postinst_configure'] = configure_uwsgi + " install"
        package_vars['prerm_remove'] = configure_uwsgi + " remove"


    package_start_time = now(args)
    deb = debian.DebianPackage(
        args.virtualenv_path,
        package_vars,
        logger=args.logger)
    if args.dry_run:
        debian_package = "%s_%s.deb" % (
            args.debian_pkgvername.replace('-', '_'), deb.architecture)
    else:
        deb.emit_debian_files()
        result = deb.build_package()
        args.logger.info('\n'.join(result))
        args.logger.notify("Debian packaging took %.2f seconds" %
                           elapsed_time(args, package_start_time))
        debian_package = deb.debian_package_file()
    target_basename = "%s_%s.deb" % (
        args.package_name.lower(), deb.architecture)
    move_output(args, debian_package, target_basename)

def package_virtualenv_rpm(args):
    args.logger.warn("--rpm not implemented yet")
    if not args.dry_run:
        pass

def package_virtualenv_squash_fs(args):
    args.logger.warn("--squash-fs not implemented yet")
    if not args.dry_run:
        pass

def package_virtualenv_tar_gzip(args):
    output_filename = utils.abspath(
        os.path.join(args.virtualenv_path, "..",
                     args.debian_pkgvername + ".tar.gz"))
    args.logger.info("Creating %s" % output_filename)
    if not args.dry_run:
        utils.make_tarfile(output_filename, args.virtualenv_path)
        move_output(args, output_filename)

def package_virtualenv_wheel(args):
    args.logger.warn("--wheel not implemented yet")
    if not args.dry_run:
        pass

def package_virtualenv_zip(args):
    output_filename = utils.abspath(
        os.path.join(args.virtualenv_path, "..",
                     args.debian_pkgvername + ".zip"))
    args.logger.info("Creating %s" % output_filename)
    if not args.dry_run:
        utils.make_zipfile(output_filename, args.virtualenv_path)
        move_output(args, output_filename)

def package_virtualenv(args):
    args.logger.notify("Packaging virtualenv")
    # Package as many different ways as requested.
    # No reason to make these mutually exclusive.
    if args.squash_fs:
        package_virtualenv_squash_fs(args)
    if args.tar_gzip:
        package_virtualenv_tar_gzip(args)
    if args.wheel:
        package_virtualenv_wheel(args)
    if args.zip:
        package_virtualenv_zip(args)
    # This leaves turds. Do last.
    if args.deb:
        package_virtualenv_debian(args)
    if args.rpm:
        package_virtualenv_rpm(args)

def delete_virtualenv(args):
    if args.delete_virtualenv:
        args.logger.info("Deleting virtualenv '%s'" % args.virtualenv_path)
        if not args.dry_run:
            shutil.rmtree(args.root_dir)
    else:
        args.logger.notify("Virtualenv kept at '%s'" % args.virtualenv_path)


def eggsac(**kwargs):
    args = initialize_args(parse_args(**kwargs))

    try:
        args.logger.notify("Creating application '%s'" % args.package_name)
        make_virtualenv(args)
        install_always_unzips_in_virtualenv(args)
        install_all_packages_in_virtualenv(args)
        generate_additional_config(args)
        relocate_virtualenv(args)
        package_virtualenv(args)
    except:
        import traceback
        traceback.print_exc()
        args.delete_virtualenv = False # Keep around for debugging
        raise
    finally:
        delete_virtualenv(args)
        args.logger.notify("Packaging took %.2f seconds" % elapsed_time(args))
