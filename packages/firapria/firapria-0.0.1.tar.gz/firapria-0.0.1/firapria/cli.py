# -*- coding: UTF-8 -*-

"""
Command-line interface
"""

import sys
import argparse
from firapria.pollution import PollutionFetcher

from colorama import init, Fore
init(autoreset=True)


def print_version_and_exit():
    from firapria import __version__
    print("firapria v%s" % __version__)
    sys.exit(0)


def colorize_indices(indices, max_value):
    def colorize(i):
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

    return map(colorize, indices)


def print_pollution():
    p = PollutionFetcher()
    print """Pollution:
    Yesterday: %s
    Today: %s
    Tomorrow: %s""" % tuple(colorize_indices(p.indices(), max_val=100))


def main():
    parser = argparse.ArgumentParser(
        description='Get pollution indices for Paris'
    )
    parser.add_argument('--pollution', dest='pollution', short='-p',
                        default=True, help='print pollution info')
    parser.add_argument('--version', action='store_true')
    if args.version:
        print_version_and_exit()

    if args.pollution:
        print_pollution()
