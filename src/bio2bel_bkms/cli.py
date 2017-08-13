# -*- coding: utf-8 -*-

import sys

import click

from .run import write_bel


@click.group()
def main():
    """Tools for writing BKMS"""


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
def write(output):
    """Writes BKMS to file"""
    write_bel(output)


if __name__ == '__main__':
    main()
