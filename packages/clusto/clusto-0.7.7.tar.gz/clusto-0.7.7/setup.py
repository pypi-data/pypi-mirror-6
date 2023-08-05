#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Clusto cluster management tool
# Copyright 2009, Ron Gorodetzky ron@parktree.net

import os
import setuptools
import sys


srcdir = os.path.join(os.path.dirname(sys.argv[0]), 'src')
reqs = os.path.join(os.path.dirname(sys.argv[0]), 'requirements.txt')

setuptools.setup(
    name = "clusto",
    version = "0.7.7",
    packages = setuptools.find_packages('src'),
    author = "Ron Gorodetzky",
    author_email = "ron@parktree.net",
    license = 'BSD',
    description = "Cluster management and inventory system",
    install_requires=[
        _.strip()
        for _ in open(reqs).readlines()
        if _ and not _.startswith('#')
    ],
    entry_points = {
        'console_scripts': [
            'clusto = clusto.script_helper:main',
            'clusto-allocate = clusto.commands.allocate:main',
            'clusto-attr = clusto.commands.attr:main',
            'clusto-console = clusto.commands.console:main',
            'clusto-deallocate = clusto.commands.deallocate:main',
            'clusto-info = clusto.commands.info:main',
            'clusto-list-pool = clusto.commands.list_pool:main',
            'clusto-pool = clusto.commands.pool:main',
            'clusto-reboot = clusto.commands.reboot:main',
            'clusto-rename = clusto.commands.rename:main',
            'clusto-initdb = clusto.commands.initdb:main',
            'clusto-shell = clusto.commands.shell:main',
            'clusto-list-all = clusto.commands.list_all:main',
        ],
    },
    zip_safe = False,
    package_dir = { '': 'src' },
    scripts = [
        os.path.join(srcdir, 'scripts', 'clusto-tree'),
        os.path.join(srcdir, 'scripts', 'clusto-update-info'),
        os.path.join(srcdir, 'scripts', 'clusto-update-db'),
        os.path.join(srcdir, 'scripts', 'clusto-dhcpd'),
        os.path.join(srcdir, 'scripts', 'clusto-httpd'),
      ],
      test_suite = "clusto.test.alltests.gettests",
)

