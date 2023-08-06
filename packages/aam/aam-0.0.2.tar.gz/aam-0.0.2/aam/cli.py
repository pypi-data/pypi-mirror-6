#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

from .utils import *
from .options import *

from reader.reader import *
from generator.render import *

import aam

doc = """Aam v%s
Usage:
    aam init
    aam build
    aam -h | --help
    aam --version

Options:
    -h --help               Show this screen and exit.
""" % aam.__version__

from parguments import Parguments

parguments = Parguments(doc, version=aam.__version__)

def pre_init():
    hub.root.path = os.path.dirname(__file__)
    hub.root.template_path = os.path.join(os.path.dirname(__file__),'templates')
    hub.root.static_path = os.path.join(os.path.dirname(__file__), 'static')
    hub.site.path = os.getcwd()
    hub.site.page_path = os.path.join(hub.site.path, 'pages')
    hub.site.deploy_path = os.path.join(hub.site.path, 'deploy')

@parguments.command
def init():
    """
    Usage:
        aam init

    Options:
        -h --help               Show this screen and exit.
    """
    pre_init()
    mkdir("pages")
    mkdir("deploy")
    shutil.copyfile(os.path.join(hub.root.path, 'config.ini'), 'config.ini')
    shutil.copytree(hub.root.static_path, os.path.join(hub.site.deploy_path, "static"))
    print("Please edit config.py to config your site")

@parguments.command
def build():
    """
    Usage:
        aam build

    Options:
        -h --help               Show this screen and exit.
    """
    pre_init()
    read_config()
    read_page()
    render()

def main():
    parguments.run()
