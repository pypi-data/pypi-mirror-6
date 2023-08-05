""" Service that loads the qscollectors and runs them when needed to create a quantified self database"""

import argparse
import json
import sys
import qscollect.collector_base as collector_base
import qscollect.daemon as factory

import logging
logging.basicConfig(level=logging.DEBUG)


def main(args=sys.argv[1:]):
    args = _get_args(args)

    config_file = open(args.config, "r")
    config = json.load(config_file)

    _loader = collector_base.Loader()

    for collector in config["collectors"]:
        _loader.load(collector)

    daemon = factory.factory(config, _loader.collectors, daemonize=not args.foreground)

    daemon.run()


def _get_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--foreground", "-f", action="store_true")
    parser.add_argument("config", default="config.json", help="The configuration file")

    return parser.parse_args(args)