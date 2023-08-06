"""
Copyright 2013 Reed O'Brien <reed@reedobrien.com>.
All rights reserved. Use of this source code is governed by a
BSD-style license that can be found in the LICENSE file.
"""
from __future__ import unicode_literals

import argparse

DEFAULT_REGION = "us-east-1"


def setup_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-R", "--region", default=DEFAULT_REGION,
                        help="The AWS region to work in. Default: {}".format(
                            DEFAULT_REGION))
    parser.add_argument("-c", "--config", required=True, default=None,
                        help="The path to the config file")
    parser.add_argument("-d", "--dryrun", action="store_true",
                        help="Don't actually do it... just print")
    parser.add_argument("-y", "--yaml", action="store_const", const="yaml",
                        dest="format", help="Serialization in YAML format")
    parser.add_argument("-j", "--json", action="store_const", const="json",
                        dest="format", help="Serialization in JSON format")

    # dbg_or_logger = parser.add_mutually_exclusive_group()
    ## this should make a logger to feed to BTX
    ## maybe from a dict or a file...
    # dbg_or_logger.add_argument("-l", "--logger", type=????)

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Output more information")

    # output dir for creds

    return parser


def parse_args(parser):
    args = parser.parse_args()
    if not args.format:
        parser.error("One of --json (-j) or --yaml (-y) must be specified")
    return args
