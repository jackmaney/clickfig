import sys
import click
sys.path = ['..'] + sys.path

import clickfig

file = clickfig.Config("./test.json")


@click.group()
def main():
    pass


clickfig.attach(main, file)
main()
if __name__ == "__main__":
    main()
