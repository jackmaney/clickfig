import click


def attach(group, config, command_name="config"):
    """
    Takes a :class:`ConfigFile` object and click ``Group`` object and attaches the former as a command to the latter.

    :param click.Group group: A `Group object within click <http://click.pocoo.org/api/#click.Group>`_ to which
     our configuration command will be attached.
    :param clickfig.Config config: A configuration object.
    :param command_name:
    """

    if not isinstance(group, click.Group):
        raise ValueError("group must be a click.Group object (not {})".format(type(group)))

    @group.command(name=command_name)
    @click.argument("key", required=False)
    @click.argument("value", required=False)
    @click.option("--unset", is_flag=True, default=False)
    def config_cmd(key, value, unset, level=None):

        if level is None:
            obj = config
        else:
            obj = config.file_by_level(level)

        if value is None:

            if unset and key is not None:
                obj.unset(key)
            elif unset:
                raise ValueError("Cannot unset without a key")
            else:

                read_results = obj.read(key=key)
                if not isinstance(read_results, list):
                    read_results = [read_results]

                print("\n".join([str(x) for x in read_results]))
        else:
            obj.write(key, value)

    if len(config.config_files) > 1:
        for lvl in [f.get("level") for f in config.file]:
            config_cmd = click.option("--{}".format(lvl), "level",
                                      flag_value=lvl)(config_cmd)

    return config_cmd
