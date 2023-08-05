# coding=utf8

"""cli interface"""


import logging
import sys
from .utils import join
from os.path import dirname
from .logger import logger
from .server import server
from . import version
from .generator import generator
from .daemon import lilac_daemon
from subprocess import call
from docopt import docopt


def task(task_func):
    def wrapper(*args, **kwargs):
        if task_func.__doc__:
            logger.info(task_func.__doc__)
        return task_func(*args, **kwargs)
    return wrapper


@task
def deploy():
    """deploy blog: less/, src/post/, config.toml, Makefile"""
    lib_dir = dirname(__file__)  # this library's directory
    res = join(lib_dir, "resources")
    call("rsync -aqu " + join(res, "*") + " .", shell=True)
    logger.success("deploy done")
    logger.info("Please edit config.toml to meet tour needs")
    logger.info("Run 'make build' to build blog to htmls")
    logger.info("Run 'make clean' to remove built htmls")


@task
def clean():
    """rm -rf post page tag 404.html about.html archives.html feed.atom index.html tags.html"""
    paths = [
        "post",
        "page",
        "tag",
        "404.html",
        "about.html",
        "archives.html",
        "feed.atom",
        "index.html",
        "tags.html"
    ]

    cmd = ["rm", "-rf"] + paths
    call(cmd)
    logger.success("clean done")


def main():
    """Usage:
  lilac serve [<port>] [--watch]
  lilac (deploy|build|clean)
  lilac (start|stop|status|restart)
  lilac [-h|-v]

Options:
  -h --help     show this help message
  -v --version  show version
  --watch       watch source files for changes
  <port>        which port for server to use(default: 8888)

Commands:
  deploy        deploy blog in current directory
  build         build source files to htmls
  clean         remove files built by lilac
  serve         start a web server, as a option, start watching
  start         start http server and auto rebuilding as a daemon running in the background
  stop          stop the http server and auto rebuilding daemon
  restart       restart http server and auto rebuilding daemon
  status        report the status of the daemon"""

    arguments = docopt(main.__doc__, version='lilac version: ' + version)
    # set logger's level to info
    logger.setLevel(logging.INFO)

    if arguments["deploy"]:
        deploy()
    elif arguments["clean"]:
        clean()
    elif arguments["build"]:
        generator.generate(localhost=False)  # be honest to config.toml
    elif arguments["serve"]:

        port_s = arguments["<port>"]

        if not port_s:
            port = 8888
        else:
            try:
                port = int(port_s)
            except ValueError:
                logger.error("Error format of argument 'port': '%s'" % port_s)
                sys.exit(1)

        server.run(arguments["--watch"], port)
    elif arguments["start"]:
        lilac_daemon.start()
    elif arguments["stop"]:
        lilac_daemon.stop()
    elif arguments["restart"]:
        lilac_daemon.restart()
    elif arguments["status"]:
        lilac_daemon.status()
    else:
        exit(main.__doc__)
