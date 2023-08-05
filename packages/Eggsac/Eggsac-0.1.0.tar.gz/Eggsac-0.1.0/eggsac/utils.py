# -*- coding: utf-8 -*-

from __future__ import absolute_import


import ConfigParser
import datetime
import logging
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import virtualenv
import zipfile

_devnull = os.open(os.devnull, os.O_RDWR)
PYTHON_VERSION = sys.version[:3]  # e.g., "2.7"
is_win = (sys.platform == 'win32')

def run_command(
        cmd, env=os.environ,
        logger=None, loggerName=None, log_errors=True,
        **kwargs):
    """
    Run the given command, possibly modifying it by inserting some
    convenient options, with the given environment.  Returns an array
    of lines from stdout on success; raises a
    subprocess.CalledProcessError on failure.
    """
    logger = logger or logging.getLogger(loggerName)

    # Ignore these passed-in keywords: we know better.
    kwargs = kwargs.copy()
    for kw in ['stdout', 'stderr', 'universal_newlines', 'env']:
        if kw in kwargs:
            logger.warn("run_command: Ignoring keyword %s", kw)
            del kwargs[kw]

    child = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        env=env,
        **kwargs)

    # TODO: poll child's stdout and stderr so that the parent
    # can echo output more or less in real time. It's disconcerting
    # with a slow child process, where (apparently) nothing happens
    # for several minutes, then thousands of lines of output
    # are spewed all at once.
    # See http://znasibov.info/blog/html/2010/04/24/inside_python_subprocess_communication.html

    (stdout, stderr) = child.communicate()
    retcode = child.wait()

    if retcode != 0:
        for line in stderr.splitlines():
            if log_errors:
                logger.error("%s", line)
            else:
                logger.debug("%s", line)
        raise subprocess.CalledProcessError(retcode, cmd)

    rv = stdout.splitlines() + stderr.splitlines()

    logger.debug("in %s, %s => %s",
                 kwargs.get('cwd', os.getcwd()),
                 cmd, rv)
    # TODO: return (retcode, stdout, stderr)
    return rv

class VCS(object):
    def __init__(self, root):
        self.root = root

    def __repr__(self):
        return "<%s root=%r>" % (self.__class__.__name__, self.root)

    def command(self, params, one_liner=True, *args, **kwargs):
        rv = run_command(self.Executable + params, cwd=self.root, *args, **kwargs)
        return rv[0] if rv and one_liner else rv

class Git(VCS):
    Executable = ["git"]

    @classmethod
    def find_root(cls, dir):
        try:
            relroot = subprocess.check_output(
                ["git", "rev-parse", "--show-cdup"], stderr=_devnull, cwd=dir)
            return os.path.normpath(os.path.join(dir, relroot.strip() or "."))
        except subprocess.CalledProcessError:
            return None

    def sha(self):
        return self.command(["rev-parse", "--short", "HEAD"])

    def revision(self):
        return int(self.command(["rev-list", "--count", "HEAD"]))

    def current_branch(self):
        return self.command(["rev-parse", "--abbrev-ref", "HEAD"])

class Mercurial(VCS):
    Executable = ["hg"]

    @classmethod
    def find_root(cls, dir):
        try:
            return subprocess.check_output(["hg", "root"], stderr=_devnull, cwd=dir).strip()
        except subprocess.CalledProcessError:
            return None

    def sha(self):
        return self.command(["identify", "--id"])

    def revision(self):
        return int(self.command(["identify", "--num"]))

    def current_branch(self):
        return self.command(["branch"])

def find_vcs(dir):
    for vcs in (Git, Mercurial):
        root = vcs.find_root(dir)
        if root:
            return vcs(root)
    return None

class NullContext:
    """
    A context manager that can be used in a `with` statement
    when nothing needs to be done; e.g., with(foo if bar else NullContext())
    """
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass

class FilePush(object):
    """Context Manager that temporarily creates a file at `path` with `contents`,
    which is removed on exit. If there was already a file called `path`,
    it is preserved."""
    def __init__(self, path, content):
        self.path, self.content, self.old_path = path, content, None

    def __enter__(self):
        if os.path.exists(self.path):
            # Possible race condition where some other process
            # grabs `old_path`, but I don't care.
            self.old_path = tempfile.mktemp()
            shutil.move(self.path, self.old_path)
        with open(self.path, 'wb') as f:
            f.write(self.content)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.path)
        if self.old_path:
            shutil.move(self.old_path, self.path)

def replace_lines(lines, replacements):
    replacements = [(re.compile(p), r) for p,r in replacements]
    return [p.sub(r, line) for line in lines for p,r in replacements]

def file_replace_lines(filename, replacements):
    """Replaces lines in `filename` with `replacements`,
    a sequence of (uncompiled regex, substition) pairs."""
    with open(filename, 'rb') as f:
        lines = f.read().decode('utf-8').splitlines()
    lines = replace_lines(lines, replacements)
    with open(filename, 'wb') as f:
        f.write('\n'.join(lines).encode('utf-8'))

def create_virtualenv(venv_dir, use_distribute=False, unzip_setuptools=True, **kwargs):
    venv_copyfile = virtualenv.copyfile
    try:
        # Monkeypatch virtualenv to force stdlibs to be copied, not symlinked
        virtualenv.copyfile = lambda src, dst, symlink=True: venv_copyfile(
            src, dst, symlink=False)
        virtualenv.create_environment(
            venv_dir,
            unzip_setuptools=unzip_setuptools,
#           use_distribute=use_distribute, # Only for virtualenv <= 1.9
            never_download=True,
            **kwargs)
    finally:
        virtualenv.copyfile = venv_copyfile

def valid_virtualenv_dir(venv_dir):
    activate = ("Scripts", "activate.bat") if is_win else ("bin", "activate")
    return venv_dir and os.path.exists(os.path.join(venv_dir, *activate))

def virtualenv_python_exe(venv_dir):
    python_exe = ("Scripts", "python.exe") if is_win else ("bin", "python")
    return os.path.join(venv_dir, *python_exe)

def cleanup_virtualenv(venv_dir):
    # Clean up some large stuff we won't need
    for dir in [
            "include",
            os.path.join("lib", "python"+PYTHON_VERSION, "config"),
    ]:
        subdir = os.path.join(venv_dir, dir)
        if os.path.exists(subdir):
            shutil.rmtree(subdir)

def check_virtualenv(venv_dir):
    if not venv_dir:
        venv_dir = os.getenv('VIRTUAL_ENV')
        if not venv_dir:
#           print "Must supply virtualenv or run under one"
            return None

    if not valid_virtualenv_dir(venv_dir):
        # Using virtualenvwrapper?
        if os.getenv("WORKON_HOME"):
            venv_dir = os.path.join(os.getenv("WORKON_HOME"), venv_dir)

    if not valid_virtualenv_dir(venv_dir):
#       print "Can't find virtualenv", venv_dir
        return None
    else:
        return venv_dir

def fake_virtualenv(venv_dir):
    """Fake the effect of 'source activate' for use with subprocess.Popen"""
    # Note: Can't use
    #    activate_this = os.path.join(venv_dir, "bin", "activate_this.py")
    #    execfile(activate_this, dict(__file__=activate_this))
    # as that affects the *current* Python
    bin_path = r"\Scripts;" if is_win else "/bin:"
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = venv_dir
    env['PATH'] = venv_dir + bin_path + env['PATH']
    if 'PYTHONHOME' in env:
        del env['PYTHONHOME']
    # Don't bother with PS1 or PROMPT, as this is for a non-interactive shell
    return env

_interesting_env_vars = ('PATH', 'PYTHONPATH', 'VIRTUALENV')

def site_packages_path(venv_dir, python_version=None):
    return os.path.join(
        venv_dir or '',
        "lib",
        "python%s" % python_version or PYTHON_VERSION,
        "site-packages")

def find_egg(venv_dir, package_name, relative=False, python_version=None):
    python_version = python_version or PYTHON_VERSION
    egg_suffix = "-py%s.egg" % python_version
    packages_path = site_packages_path(venv_dir, python_version)
    site_packages = os.listdir(packages_path)
    match = [egg for egg in site_packages
             if egg.startswith(package_name) and egg.endswith(egg_suffix)]

    if not match:
        raise ValueError("Can't find '%s*%s' in %s" %
                         (package_name, egg_suffix, packages_path))
    elif len(match) > 1:
        raise ValueError("Too many matches for %s in %s: %r" %
                         (package_name, packages_path, match))
    else:
        return os.path.join(
            site_packages_path('' if relative else venv_dir, python_version),
            match[0])

def make_activate_relative(venv_dir):
    # In bin/activate, replace hard-coded
    #   VIRTUAL_ENV="/path/to/virtualenv"
    # with location-agnostic
    #   VIRTUAL_ENV="$(cd $(dirname "$BASH_SOURCE")/..; pwd)"
    # For zsh, use $0 instead of $BASH_SOURCE
    file_replace_lines(
        os.path.join(venv_dir, "bin", "activate"),
        [(r'^VIRTUAL_ENV=".*"$',
          'VIRTUAL_ENV="$(cd $(dirname "$BASH_SOURCE")/..; pwd)"')]
    )

def setup_cfg_context_manager(index_url, dir):
    """Temporarily create dir/setup.cfg, setting index_url to speed up package download"""
    if index_url:
        contents = "[easy_install]\nindex_url=%s\n" % urlify(index_url)
        return FilePush(os.path.join(dir, "setup.cfg"), contents)
    else:
        return NullContext()

def abspath(path):
    return os.path.abspath(os.path.expanduser(path))

def urlify(path):
    if (path.startswith("http://")
        or path.startswith("https://")
        or path.startswith("file://")):
        return path
    else:
        return "file://" + abspath(path)

def tar_compression_mode(filename):
    if filename.endswith(".tar.gz") or filename.endswith(".tgz"):
        return ":gz"
    elif filename.endswith(".tar.bz2") or filename.endswith(".tbz2"):
        return ":bz2"
    else:
        return ""

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w"+tar_compression_mode(output_filename)) as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def zip_add_directory(zip, source_dir):
    """Recursively add a directory tree to `zip`, an archive."""
    relroot = abspath(os.path.join(source_dir, ".."))
    for root, dirs, files in os.walk(source_dir):
        # add directory `root` (needed for empty dirs)
        zip.write(root, os.path.relpath(root, relroot))
        for file in files:
            filename = os.path.join(root, file)
            if os.path.isfile(filename): # regular files only
                arcname = os.path.join(os.path.relpath(root, relroot), file)
                zip.write(filename, arcname)

def make_zipfile(output_filename, source_dir):
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
        zip_add_directory(zip, source_dir)

def make_dir(target_dir):
    if os.path.exists(target_dir):
        if not os.path.isdir(target_dir):
            raise ValueError("'%s' is not a directory" % target_dir)
    else:
        os.makedirs(target_dir)

def move_file_to_dir(source_file, target_dir, target_basename=None):
    make_dir(target_dir)
    target_dir = abspath(target_dir)
    target_file = os.path.join(
        target_dir, target_basename or os.path.basename(source_file))
    if os.path.exists(target_file):
        os.remove(target_file)
    shutil.move(source_file, target_file)
    return target_file

def timestamp(dt=None, precision=3):
    dt = dt or datetime.datetime.now()
    return dt.strftime("%H:%M:%S.%f")[:-precision]

def read_ini(package_dir, ini_filename, required=True):
    ini_path = os.path.join(package_dir, ini_filename)
    cfg = ConfigParser.ConfigParser()
    read_ok = cfg.read(ini_path)
    if required and not read_ok:
        raise ValueError("Could not read '%s'" % ini_path)
    return cfg

def read_list(cfg, section, option):
    multiline = cfg.get(section, option)
    return filter(None, [x.strip() for x in multiline.splitlines()])
