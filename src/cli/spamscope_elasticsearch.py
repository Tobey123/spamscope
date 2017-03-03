#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2017 Fedele Mantuano (https://twitter.com/fedelemantuano)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import logging
import os
import runpy
import sys
import time

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError


current = os.path.realpath(os.path.dirname(__file__))
__version__ = runpy.run_path(
    os.path.join(current, "..", "options.py"))["__version__"]

# Logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)


def get_args():
    parser = argparse.ArgumentParser(
        description="It manages SpamScope topologies",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(help="sub-commands", dest="subparser")

    # Common args
    parser.add_argument(
        "-c",
        "--client-host",
        default="elasticsearch",
        help="Elasticsearch client host",
        dest="client_host")

    # Common args
    parser.add_argument(
        "-m",
        "--max-retry",
        default=10,
        type=int,
        help="Max retry for action",
        dest="max_retry")

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__))

    # Submit args
    replicas = subparsers.add_parser(
        "replicas", help="Update the number of replicas")

    replicas.add_argument(
        "-n",
        "--nr-replicas",
        default=0,
        type=int,
        help="Number of replicas.",
        dest="nr_replicas")

    replicas.add_argument(
        "-i",
        "--index",
        default="_all",
        help=("A comma-separated list of index names; use _all "
              "or empty string to perform the operation on all indices."),
        dest="index")

    return parser.parse_args()


def update_nr_replicas(client_host, max_retry, nr_replicas, index):

    for i in range(1, max_retry):
        try:
            es = Elasticsearch(hosts=client_host)
            es.indices.put_settings(
                body={"index": {"number_of_replicas": int(nr_replicas)}},
                index=index)
            log.info("Update replicas done")
            return

        except ConnectionError:
            log.warning("Update replicas failed. Waiting for {} sec".format(i))
            time.sleep(i)

    log.error("Update replicas definitely failed")


def main():
    # Command line args
    args = get_args()

    # replicas
    if args.subparser == "replicas":
        update_nr_replicas(
            client_host=args.client_host,
            max_retry=args.max_retry,
            nr_replicas=args.nr_replicas,
            index=args.index)


if __name__ == "__main__":
    main()
