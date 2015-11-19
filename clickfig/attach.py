import click


def attach(group, config_file, command_name="config"):
    """
    Takes a :class:`ConfigFile` object and click ``Group`` object and attaches the former as a command to the latter.

    :param click.Group group: A `Group object within click <http://click.pocoo.org/api/#click.Group>`_ to which
     our configuration command will be attached.
    :param clickfig.ConfigFile config_file: A configuration file object.
    :param command_name:
    """

    if not isinstance(group, click.Group):
        raise ValueError("group must be a click.Group object (not {})".format(type(group)))

    @group.command(command_name)
    @click.argument("key", required=False)
    @click.argument("value", required=False)
    def config_cmd(key, value):
        if value is None:
            print(config_file.read(key=key))
        else:
            config_file.write(key, value)
