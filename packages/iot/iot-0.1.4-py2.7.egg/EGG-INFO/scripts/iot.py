#!/usr/bin/python

from __future__ import unicode_literals
from future.builtins import open

from distutils.dir_util import copy_tree
from optparse import OptionParser
import os
from shutil import move
from uuid import uuid4

from django.utils.importlib import import_module


def path_for_import(name):
    """
    Returns the directory path for the given package or module.
    """
    return os.path.dirname(os.path.abspath(import_module(name).__file__))


def import_dotted_path(path):
    """
    Takes a dotted path to a member name in a module, and returns
    the member after importing it.
    """
    try:
        module_path, member_name = path.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, member_name)
    except (ValueError, ImportError, AttributeError) as e:
        raise ImportError("Could not import the name: %s: %s" % (path, e))

def create_project():
    """
    Copies the contents of the project_template directory to a new
    directory specified as an argument to the command line.
    """

    parser = OptionParser(usage="usage: %prog [options] project_name")
    parser.add_option("-a", "--alternate", dest="alt", metavar="PACKAGE",
        help="Alternate package to use, containing a project_template")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("project_name must be specified")
    project_name = args[0]
    if project_name.startswith("-"):
        parser.error("project_name cannot start with '-'")
    project_path = os.path.join(os.getcwd(), project_name)

    # Ensure the given directory name doesn't clash with an existing
    # Python package/module.
    try:
        __import__(project_name)
    except ImportError:
        pass
    else:
        parser.error("'%s' conflicts with the name of an existing "
                     "Python module and cannot be used as a project "
                     "name. Please try another name." % project_name)

    # Create the list of packages to build from - at this stage it
    # should only be one or two names, mezzanine plus an alternate
    # package.
    packages = ["iot"]
    if options.alt:
        packages.append(options.alt)
    for package_name in packages:
        try:
            __import__(package_name)
        except ImportError:
            parser.error("Could not import package '%s'" % package_name)

    # Build the project up copying over the project_template from
    # each of the packages. An alternate package will overwrite
    # files from Mezzanine.
    for package_name in packages:
        package_path = path_for_import(package_name)
        copy_tree(os.path.join(package_path, "../osiot"), project_path)

    # Clean up pyc files.
    for (root, dirs, files) in os.walk(project_path, False):
        for f in files:
            try:
                if f.endswith(".pyc"):
                    os.remove(os.path.join(root, f))
            except:
                pass

if __name__ == "__main__":
    create_project()