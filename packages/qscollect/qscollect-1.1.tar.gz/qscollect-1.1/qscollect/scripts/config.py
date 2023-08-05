""" Configures a collector as part of the QSCollect system """

import sys
import pkgutil
import types
import argparse

COLLECTOR_REGISTRY = []
import qscollect.collectors as collectors
import qscollect.db as qsdb

def options(args):
    discover_collectors()

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(help="Collectors")

    for collector in COLLECTOR_REGISTRY:
        subparser = subparsers.add_parser(collector.Meta.name, help=collector.__doc__)
        getattr(collector, "config_args", lambda x: None)(subparser)
        subparser.set_defaults(
            _config=getattr(collector, "config"),
            _class=collector
        )

    return parser.parse_args(args)

def main(args=sys.argv[1:]):
    opt = options(args)
    values = opt._config(opt)

    db = qsdb.db()
    db.set_config(opt._class.Meta.name, opt._class.Meta.style, values)

def discover_collectors():
    global COLLECTOR_REGISTRY

    COLLECTOR_REGISTRY = []

    for importer, name, skip in pkgutil.walk_packages(collectors.__path__,
                                                      collectors.__name__ + "."):
        if skip:
            continue

        valid_module, objects = examine_module(importer, name)
        if not valid_module:
            continue

        COLLECTOR_REGISTRY.extend(objects)

def examine_module(importer, name):
    if name.split('.')[-1].startswith('_'):
        return False, []

    loader = importer.find_module(name)
    module = loader.load_module(loader.fullname)

    objects = (getattr(module, x) for x in dir(module))
    objects = (x for x in objects if type(x) == types.TypeType)
    objects = list((x for x in objects if hasattr(x, 'config')))

    return len(objects) > 0, objects