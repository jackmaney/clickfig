"""
This example is a bit more complex, and simulates a CLI app that might be used
to contact and run jobs on a server. The config options are used in multiple commands.
"""
from __future__ import absolute_import, print_function

import sys
from random import random
from time import sleep

import click
from six.moves import urllib

sys.path = ['../..'] + sys.path

import clickfig

cfg = clickfig.Config("./server.ini")


def get_url(username=None, password=None):
    """
    This isn't part of the CLI application per se,
    but it does something that's accomplished in more
    than one function below: namely, grabbing the pieces
    of the fake server URL and putting them together.

    So, it's here for DRY purposes.
    :param str|None username: A username that overrides the one given in the config file.
    :param str|None password: A password that overrides the one given in the config file.
    :return: The URL with login info included (and URL-escaped).
    :rtype: str
    """

    url = str(cfg.read("server.url"))
    port = str(cfg.read("server.port"))

    username = username or str(cfg.read("login.username"))
    password = password or str(cfg.read("login.password"))

    # URL escape
    username = urllib.parse.quote(username)
    password = urllib.parse.quote(password)

    if not url.startswith("http://") and not url.startswith("https://"):
        raise ValueError("server.url must be HTTP or HTTPS.")

    protocol, remaining_url = url.split("//", 1)

    return "{protocol}//{username}:{password}@{remaining_url}:{port}".format(
        protocol=protocol, username=username, password=password,
        remaining_url=remaining_url, port=port
    )


@click.group()
@click.option("--username", "-U", type=str, default=None, help="Username (overrides the username in the config file)")
@click.option("--password", "-p", type=str, default=None, help="Password (overrides the password in the config file)")
@click.pass_context
def main(context, username, password):
    """A fake utility for communicating with a server. Look at ./server.ini"""
    context.obj["username"] = username
    context.obj["password"] = password


@main.command()
@click.pass_context
def connect(context):
    """Pretend to connect to the server..."""
    print("Connecting to {}".format(get_url(username=context.obj["username"], password=context.obj["password"])))


@main.command()
@click.pass_context
def ping(context):
    """Pretend to ping the server..."""
    url = get_url(username=context.obj["username"], password=context.obj["password"])
    print("Pinging {}...".format(url))
    for i in range(4):
        # Between 10 and 25 ms
        duration = 0.01 + 0.015 * random()
        sleep(duration)
        print("64 bytes from 127.0.0.1: icmp_seq=4 ttl=55 time={0:.3f} ms".format(1888 * duration))
    print("Done!")


@main.command()
@click.option("--file", "-f", type=str, help="The file to upload")
@click.pass_context
def upload(context, file):
    """Pretend to upload a file to the server...for some reason..."""
    url = get_url(username=context.obj["username"], password=context.obj["password"])
    print("Pretending to run:\n\ncurl - X POST - d @{} {}".format(file, url))
    sleep(0.75)
    print("Done!")


clickfig.attach(main, cfg)

if __name__ == "__main__":
    main(obj={})
