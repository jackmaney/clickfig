import sys
import click
sys.path = ['..'] + sys.path

import clickfig

file = clickfig.Config("./test.ini")


@click.group()
def main():
    pass


clickfig.attach(main, file)

if __name__ == "__main__":
    main()
