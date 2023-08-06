#! /usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'mackaiver'

#Lets start with a simple commandline tool
import argparse
import os

from colorama import init, Fore, Style

from seins.PageParser import DBPageParser, PageContentError
from seins.HtmlFetcher import FetcherException

#init colorama so it works on windows as well.
#The autoreset flag keeps me from using RESET on each line I want to color
init(autoreset=True)

import logging
#create a logger for this module
logger = logging.getLogger(__name__)
#the usual formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# create a handler and make it use the formatter
handler = logging.StreamHandler()
handler.setFormatter(formatter)
# now tell the logger to use the handler
logger.addHandler(handler)
logger.propagate = False


def is_valid_file(parser, arg):
    (folder, t) = os.path.split(arg)
    #logger.debug('given path is:' + os.path.split(arg))

    if not folder == '' and not os.path.exists(folder):
        parser.error("The folder %s does not exist!" % folder)
    else:
        return arg


def parse_args():
    p = argparse.ArgumentParser(description='Lecker data fetching from EFA via the commandline. ',
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    p.add_argument('-d', default='Universität s-Bahnhof, Dortmund', metavar='--departing_station', type=str,
                   help='Name of the departing station')
    p.add_argument('-a', default='Dortmund hbf', metavar='--arrival_station', type=str,
                   help='Name of the arrival station')

    p.add_argument('-o', metavar='--output', type=lambda path: is_valid_file(p, path), help='will write the html '
                                                                                            'fetched from the dbwebsite'
                                                                                            ' to the given path')

    p.add_argument('-v', action="store_true", help='Show some debug and info logging output')
    p.add_argument('-s', action="store_true", help='only display S-Bahn connections')

    args = p.parse_args()
    #check for debug logging
    if args.v:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARN)

    return args.o, args.d, args.a, args.s


def main():
    (output_path, departure, arrival, sbahn_only) = parse_args()
    connections = []

    try:
        page = DBPageParser(departure, arrival)
        connections = page.connections
        if output_path:
            with open(output_path, 'wt') as file:
                file.write(page.html)
                logger.info("Output written to " + output_path)

    except PageContentError as e:
        logger.error('Webpage returned an error message: ' + str(e))
    except FetcherException as e:
        logger.error('Fetcher could not get valid response from server: ' + str(e))

    #do some pretty printing
    print('Connections from: ' + Style.BRIGHT + departure + Style.RESET_ALL +
          '  to: ' + Style.BRIGHT + arrival)

    print(' departure, arrival, delay, connection')
    for (d, a, delay, t) in connections:
        if sbahn_only and not t.strip() is 'S':
            continue

        if delay and int(delay) >= 5:
            print(d + ',    ' + a + ',    ' + Fore.RED + delay + Fore.RESET + ',    ' + t)
        else:
            print(d + ',    ' + a + ',    ' + str(delay) + ',    ' + t)


if __name__ == '__main__':
    main()

