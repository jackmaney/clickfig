import sys
import click
sys.path = ['../..'] + sys.path

import clickfig

cfg = clickfig.Config("./test.json")


@click.group()
def main():
    pass


clickfig.attach(main, cfg)
main()
if __name__ == "__main__":
    main()
