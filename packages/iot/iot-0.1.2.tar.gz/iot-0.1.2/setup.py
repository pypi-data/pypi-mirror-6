#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import sys
import iot.pkg_info
from setuptools import setup, find_packages


if float("%d.%d" % sys.version_info[:2]) < 2.5 or float("%d.%d" % sys.version_info[:2]) >= 3.0:
	sys.stderr.write("Your Python version %d.%d.%d is not supported.\n" % sys.version_info[:3])
	sys.stderr.write("iotcmd requires Python between 2.4 and 3.0.\n")
	sys.exit(1)

source_dir_list = []
package_list = []
data_file_dict = {}
data_file_list = []
for dir in os.listdir(os.getcwd()):
    if os.path.exists(os.path.join(dir, '__init__.py')):
        package_list.append(dir)
        source_dir_list.append(dir)

for source_dir in source_dir_list:
    for rootDir, dirs, files in os.walk(source_dir):
        for dir in dirs:
            dir = os.path.join(rootDir, dir)
            if os.path.exists(os.path.join(dir, '__init__.py')):
                package_list.append(dir.replace(os.sep, '.'))
        for file in files:
            file = os.path.join(rootDir, file)
            if not file.endswith('.py') and not file.endswith('.pyc') and '.svn' not in file:
                if rootDir not in data_file_dict.keys():
                    data_file_dict[rootDir] = [file]
                else:
                    data_file_dict[rootDir].append(file)

for k, v in data_file_dict.items():
    data_file_list.append((k, v))

setup(
	name = iot.pkg_info.package,
	version = iot.pkg_info.version,
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    data_files=data_file_list,

	author = "Phodal.Gmszone",
	author_email = "gmszone@gmail.com",
	url = iot.pkg_info.url,
	license = iot.pkg_info.license,
	description = iot.pkg_info.short_description,
	long_description = iot.pkg_info.long_description,
	

		scripts=[
			'bin/iot.py',
		],
	)
