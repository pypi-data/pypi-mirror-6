#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""Create a deployable Debian package for an Eggsac."""

import codecs
import datetime
import email.utils
import os
import platform
import shutil
import socket

import utils


class DebianPackage(object):
    """Create a Debian Package from a directory tree."""
    def __init__(self, root, package_vars, logger=None):
        self.root = root
        self.logger = logger
        self.root_prefix = package_vars.pop('root_prefix', '')
        self.architecture = package_vars.pop(
            'architecture', self.debian_architecture())
        self.copyright_date = package_vars.pop(
            'copyright_date', datetime.date.today().strftime("%Y"))
        self.date822 = package_vars.pop(
            'date822', self.date_rfc822_format())
        self.distname = "unstable"
        self.eggsac_version = "0.1"  # FIXME
        self.maintainer = package_vars.pop(
            'maintainer', self.guess_maintainer())
        self.long_description = self.format_long_description(
            package_vars.pop('long_description', ''))

        self.depends = ", ".join(
            ["${misc:Depends}", "${python:Depends}"]
            + package_vars.pop('depends', []))
        self.postinst_configure = package_vars.pop('postinst_configure', '')
        self.prerm_remove = package_vars.pop('prerm_remove', '')

        for k, v in package_vars.iteritems():
            setattr(self, k, v)
        self.target_root = self.root_prefix + self.package

    def emit_debian_files(self):
        debroot = os.path.join(self.root, "debian")
        shutil.rmtree(debroot, ignore_errors=True)
        for filename, mode, template in self.DEBIAN_FILES:
            target = os.path.join(debroot, filename)
            payload = template % self.__dict__
            parent, _ = os.path.split(target)
            if not os.path.exists(parent):
                os.makedirs(parent, 0755)
            with codecs.open(target, "w", encoding="utf-8") as f:
                f.write(payload)
            os.chmod(target, mode)

    def build_package(self):
        return utils.run_command(
            ["dpkg-buildpackage", "-us", "-uc"],
            cwd=self.root,
            logger=self.logger)

    def debian_package_file(self):
        """Guess at the generated '.deb' package filename,
        since there seems to be no other way to get it."""
        parent = os.path.abspath(os.path.join(self.root, ".."))
        package = [f for f in os.listdir(parent) if f.endswith(".deb")][0]
        return os.path.join(parent, package)

    @classmethod
    def debian_architecture(cls):
        arch = platform.machine()
        return {
            'x86_64': 'amd64',  # Sigh. Python says x86_64; Debian says amd64
            }.get(arch, arch)

    @classmethod
    def date_rfc822_format(cls, timeval=None, localtime=True, usegmt=False):
        return email.utils.formatdate(timeval, localtime, usegmt)

    @classmethod
    def guess_maintainer(cls):
        username = os.environ["USER"]
        return "%s <%s@%s>" % (username, username, socket.gethostname())

    @classmethod
    def format_long_description(cls, text):
        # TODO: indent by a space; replace blank lines with " ."; etc.
        return ''

    # Use pkg_resources.safe_name, safe_version

    # Standard files that must appear in "debian" directory
    # These templates are loosely adapted from
    # stdeb <https://github.com/astraw/stdeb> and
    # dh_make <http://www.debian.org/doc/manuals/maint-guide/dreq.en.html>.

    CHANGELOG = (
        "changelog",
        0644,
        u"""\
%(package)s (%(full_version)s) %(distname)s; urgency=low

  * source package automatically created by Eggsac %(eggsac_version)s

 -- %(maintainer)s  %(date822)s\n"""
        )

    COMPAT = (
        "compat",
        0644,
        "8\n")

    CONTROL = (
        "control",
        0644,
        u"""\
Source: %(package)s
Maintainer: %(maintainer)s
Section: unknown
Priority: optional
Build-Depends: debhelper (>= 8.0.0)
Standards-Version: 3.9.2
#Homepage: <insert the upstream URL, if relevant>
#Vcs-Git: <some Git repo url>

Package: %(package)s
Architecture: %(architecture)s
Depends: %(depends)s
Description: %(description)s
%(long_description)s
"""
        )

    # TODO: allow override of "copyright" file; e.g., GPLv3, Apache, etc
    COPYRIGHT = (
        "copyright",
        0644,
        u"""\
This package was debianized by Eggsac %(eggsac_version)s on
%(date822)s

Copyright (C) %(copyright_date)s %(maintainer)s
"""
        )

    INSTALL = (
        "install",
        0644,
        # This is the directory tree in a virtualenv
        u"""\
bin/*   %(target_root)s/bin
lib/*   %(target_root)s/lib
local/* %(target_root)s/local
README  %(target_root)s
"""
        )

    RULES = (
        "rules",
        0755,
        # TODO: use more selective rules to speed up the build.
        # There's a lot that could be omitted.
        u"""\
#!/usr/bin/make -f

# This file was automatically generated by Eggsac %(eggsac_version)s on
# %(date822)s
#export DH_VERBOSE=1

%%:
\tdh $@
"""
        )

    SOURCE_FORMAT = (
        "source/format",
        0644,
        "3.0 (native)\n"
        )

    # Package Maintainer scripts.
    # Currently skeletons adapted from dh_make.
    # TODO: customize them better

    PREINST = (
        "preinst",
        0755,
        u"""\
#!/bin/sh
# preinst script for %(package)s
#
# see: dh_installdeb(1)

set -e

# summary of how this script can be called:
#        * <new-preinst> `install'
#        * <new-preinst> `install' <old-version>
#        * <new-preinst> `upgrade' <old-version>
#        * <old-preinst> `abort-upgrade' <new-version>
# for details, see http://www.debian.org/doc/debian-policy/ or
# the debian-policy package


case "$1" in
    install|upgrade)
    ;;

    abort-upgrade)
    ;;

    *)
        echo "preinst called with unknown argument \`$1'" >&2
        exit 1
    ;;
esac

# dh_installdeb will replace this with shell code automatically
# generated by other debhelper scripts.

#DEBHELPER#

exit 0
"""
        )

    POSTINST = (
        "postinst",
        0755,
        u"""\
#!/bin/sh
# postinst script for %(package)s
#
# see: dh_installdeb(1)

set -e

# summary of how this script can be called:
#        * <postinst> `configure' <most-recently-configured-version>
#        * <old-postinst> `abort-upgrade' <new version>
#        * <conflictor's-postinst> `abort-remove' `in-favour' <package>
#          <new-version>
#        * <postinst> `abort-remove'
#        * <deconfigured's-postinst> `abort-deconfigure' `in-favour'
#          <failed-install-package> <version> `removing'
#          <conflicting-package> <version>
# for details, see http://www.debian.org/doc/debian-policy/ or
# the debian-policy package


case "$1" in
    configure)
        %(postinst_configure)s
    ;;

    abort-upgrade|abort-remove|abort-deconfigure)
    ;;

    *)
        echo "postinst called with unknown argument \`$1'" >&2
        exit 1
    ;;
esac

# dh_installdeb will replace this with shell code automatically
# generated by other debhelper scripts.

#DEBHELPER#

exit 0
"""
        )

    PRERM = (
        "prerm",
        0755,
        u"""\
#!/bin/sh
# prerm script for %(package)s
#
# see: dh_installdeb(1)

set -e

# summary of how this script can be called:
#        * <prerm> `remove'
#        * <old-prerm> `upgrade' <new-version>
#        * <new-prerm> `failed-upgrade' <old-version>
#        * <conflictor's-prerm> `remove' `in-favour' <package> <new-version>
#        * <deconfigured's-prerm> `deconfigure' `in-favour'
#          <package-being-installed> <version> `removing'
#          <conflicting-package> <version>
# for details, see http://www.debian.org/doc/debian-policy/ or
# the debian-policy package


case "$1" in
    remove|upgrade|deconfigure)
        %(prerm_remove)s
    ;;

    failed-upgrade)
    ;;

    *)
        echo "prerm called with unknown argument \`$1'" >&2
        exit 1
    ;;
esac

# dh_installdeb will replace this with shell code automatically
# generated by other debhelper scripts.

#DEBHELPER#

exit 0
"""
        )

    POSTRM = (
        "postrm",
        0755,
        u"""\
#!/bin/sh
# postrm script for %(package)s
#
# see: dh_installdeb(1)

set -e

# summary of how this script can be called:
#        * <postrm> `remove'
#        * <postrm> `purge'
#        * <old-postrm> `upgrade' <new-version>
#        * <new-postrm> `failed-upgrade' <old-version>
#        * <new-postrm> `abort-install'
#        * <new-postrm> `abort-install' <old-version>
#        * <new-postrm> `abort-upgrade' <old-version>
#        * <disappearer's-postrm> `disappear' <overwriter>
#          <overwriter-version>
# for details, see http://www.debian.org/doc/debian-policy/ or
# the debian-policy package


case "$1" in
    purge|remove|upgrade|failed-upgrade|abort-install|abort-upgrade|disappear)
    ;;

    *)
        echo "postrm called with unknown argument \`$1'" >&2
        exit 1
    ;;
esac

# dh_installdeb will replace this with shell code automatically
# generated by other debhelper scripts.

#DEBHELPER#

exit 0
"""
        )

    DEBIAN_FILES = [
        CHANGELOG,
        COMPAT,
        CONTROL,
        COPYRIGHT,
        INSTALL,
        RULES,
        SOURCE_FORMAT,
        PREINST,
        POSTINST,
        PRERM,
        POSTRM,
    ]

if __name__ == '__main__':
    import virtualenv
    import sys

    package_vars = dict(
        package="eastereggs",
        full_version="0.2",
        description="Easter Eggs (containing surprises)",
    )
    logger = virtualenv.Logger(
        [(virtualenv.Logger.level_for_integer(2), sys.stdout)])
    deb = DebianPackage(os.getcwd(), package_vars, logger)
    print deb.__dict__
    deb.emit_debian_files()
    deb.build_package()
    print "Created %s" % deb.debian_package_file()
