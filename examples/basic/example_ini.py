import sys
import click
sys.path = ['../..'] + sys.path

import clickfig

cfg = clickfig.Config("./test.ini")


@click.group()
def main():
    pass


clickfig.attach(main, cfg)

if __name__ == "__main__":
    main()
