""" Dump the data in one of your collections into a csv format

EXAMPLE:
$ qsdump -o omnifocus.csv -s localhost omnifocus

"""

import argparse
import sys
import csv

import pymongo as mongo
import qscollect.db as qsdb


def main(args=sys.argv[1:]):
    args = get_args(args)
    client = mongo.MongoClient(args.server, args.port)
    db = qsdb.db(client)
    collection = db.collection("{0}_data".format(args.data_type))
    if collection.count() == 0:
        print >> sys.stderr, "{0}_data is empty".format(args.data_type)
        return -1

    if args.query is not None:
        data = _do_query(collection, args.query)
    else:
        data = collection.find()

    fieldnames = set()
    data = list(data)  # make it so we can iterate through it multiple times
    for row in data:
        fieldnames.update(row.keys())

    stream = _get_output(args.output, args.append)
    csvfile = csv.DictWriter(stream, list(fieldnames))
    if args.append == "w":
        # Write the header if we are overwriting the file, otherwise, don't
        csvfile.writeheader()
    for row in data:
        csvfile.writerow(row)


def get_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "-o",
                        help="File to save the csv to, otherwise, stdout")
    parser.add_argument("--append", "-a", action="store_const", const="a", default="w",
                        help="If outputting to a file, append ")
    parser.add_argument("--server", "-s", default='localhost',
                        help="Mongo Server to connect to")
    parser.add_argument("--port", "-p", default=27017, type=int,
                        help="Mongo Server port to connect to")
    parser.add_argument("--query", "-q",
                        help="Json File for a find query to limit the output, see README for details")
    parser.add_argument("data_type",
                        help="Type of data to dump, translate into collection [data_type]_data")

    return parser.parse_args(args)


def _do_query(collection, query):
    pass


def _get_output(output, mode):
    return open(output, mode) if output is not None else sys.stdout

