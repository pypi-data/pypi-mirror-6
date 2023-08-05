#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# setup.py --- Setup script for flo-check-homework
# Copyright (c) 2013, 2014  Florent Rougon
#
# This file is part of flo-check-homework.
#
# flo-check-homework is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# flo-check-homework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA  02110-1301 USA.

import os, sys, subprocess, textwrap
from distutils.core import setup
import flo_check_homework       # To access flo_check_homework.version_info

PACKAGE = "flo-check-homework"  # PyPI package name
PYPKG = "flo_check_homework"    # name of the main Python package
MAIN_PROGNAME = "flo-check-homework" # name of the main program
DECORATE_PROGNAME = os.path.join("tools", "flo-check-homework-decorate-games",
                                 "flo-check-homework-decorate-games")

from flo_check_homework import __version__ as VERSION
VERSION_NOSUFFIX = '.'.join([ str(i)
                              for i in flo_check_homework.version_info[:3] ])

def main():
    # Using the Qt resource system for images wastes a lot of space and is
    # quite ugly: we need the images in the source package (for the user to
    # see or modify); with PyQt resources, they would also be translated into
    # a huge string inside a hideous .py file full of \xYY escapes which
    # takes 4 times the size of the original images (!); and if this wasn't
    # enough, the .py file would be byte-compiled into a .pyc file that has
    # approximately the same size as the original images.
    # Therefore, we are loading the images by means of pkgutil.get_data()
    # instead. This unfortunately implies that they will be stored in the same
    # directory (or zip file or egg...) as PYPKG. This is not the best
    # location according to the FHS, but will be fixed when distutils2 becomes
    # usable (if ever).
    #
    # create_resource_file("fch_resources.qrc",
    #                      os.path.join(PYPKG, "fch_resources.py"))
    with open("README.rst", "r", encoding="utf-8") as f:
        long_description = f.read()

    setup(name=PACKAGE,
          version=VERSION,
          description="A program that allows to run other programs only after "
          "a set of questions have been correctly answered",
          long_description=long_description,
          author="Florent Rougon",
          author_email="f.rougon@free.fr",
          url="http://people.via.ecp.fr/~flo/",
          download_url=\
              "http://people.via.ecp.fr/~flo/projects/flo-check-homework/"
          "dist/{}/{}-{}.tar.bz2".format(VERSION_NOSUFFIX, PACKAGE, VERSION),
          keywords=[PACKAGE, "education", "learning", "calculus", "grammar"],
          requires=["PyQt4 (>=4.9)"],
          classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Development Status :: 5 - Production/Stable",
            "Environment :: X11 Applications :: Qt",
            "Environment :: Win32 (MS Windows)",
            "Environment :: MacOS X",
            "Intended Audience :: Education",
            "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
            "Operating System :: OS Independent",
            "Topic :: Education :: Computer Aided Instruction (CAI)"],
          packages=[PYPKG, "{0}.conjugations".format(PYPKG)],
          package_data={PYPKG: ["translations/*/*.qm",
                                "images/*.png",
                                "images/logo/*.png",
                                "images/rewards/10-abysmal/*.jpg",
                                "images/rewards/20-not_good_enough/*.jpg",
                                "images/rewards/20-not_good_enough/*.png",
                                "images/rewards/30-happy/*.jpg",
                                "images/rewards/30-happy/*.png",
                                "images/rewards/40-very_happy/*.jpg",
                                "images/rewards/40-very_happy/*.png"]},
          scripts=[MAIN_PROGNAME, DECORATE_PROGNAME])

if __name__ == "__main__": main()
