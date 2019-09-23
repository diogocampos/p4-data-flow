#!/usr/bin/env python3

import argparse
import json

from p4df.compute_checksum import do_compute_checksum
from p4df.data_flow import DataFlow
from p4df.deparsers import do_deparsers
from p4df.headers import do_headers
from p4df.parsers import do_parsers
from p4df.pipelines import do_pipelines


def parse_argv(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('jsonfile', type=argparse.FileType('r'),
        help='compiled P4 program')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='display all paths and variables')
    parser.add_argument('-s', '--simple', action='store_true',
        help='display only variables with possible bugs')
    parser.add_argument('-d', '--no-drops', action='store_true',
        help='omit paths with dropped packets')
    parser.add_argument('-g', '--graph', action='store_true',
        help='display graph structure')

    return parser.parse_args(argv[1:])


def main(argv):
    args = parse_argv(argv)

    with args.jsonfile as file:
        p4 = json.load(file)

    flow = get_flow(p4)

    if args.graph:
        print_graph(flow)
    else:
        print_flow(flow, args)


def get_flow(p4):
    flow = DataFlow()
    do_headers(p4, flow)
    do_parsers(p4, flow)
    do_pipelines(p4, flow)
    do_compute_checksum(p4, flow)
    do_deparsers(p4, flow)
    return flow


def print_flow(flow, options):
    for result in flow.formatted_results(options):
        if result: print('', result, sep='\n')


def print_graph(flow):
    graph = flow.format_graph()
    print(graph)


if __name__ == '__main__':
    import sys
    result = main(sys.argv)
    sys.exit(result)
