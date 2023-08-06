# -*- coding: UTF-8 -*-

"""
Command-line interface
"""

from __future__ import print_function
import sys
import argparse
from firapria.pollution import get_indices

from colorama import init, Fore
init(autoreset=True)


def print_version_and_exit():
    from firapria import __version__
    print("firapria v%s" % __version__)
    sys.exit(0)


def colorize_indice(i, max_value):
    c = Fore.RESET

    if i >= max_value:
        c = Fore.YELLOW
    elif i > 0.75 * max_value:
        c = Fore.RED
    elif i > 0.5 * max_value:
        c = Fore.MAGENTA
    elif i > 0.25 * max_value:
        c = Fore.GREEN
    else:
        c = Fore.WHITE

    return "%s%d%s" % (c, i, Fore.RESET)


def print_pollution():
    days = ['Yesterday', 'Today', 'Tomorrow']

    indices = zip(days, get_indices())

    print("Pollution:")
    for day, indice in indices:
        print("\t%s: %s" % (day, colorize_indice(indice, 100)))


def main():
    parser = argparse.ArgumentParser(
        description='Get pollution indices for Paris'
    )
    parser.add_argument('--version', '-v', action='store_true')
    args = parser.parse_args()
    if args.version:
        return print_version_and_exit()

    print_pollution()
