#!/usr/bin/env python

"""Make queries using OGRe directly.

usage: ogre [--keys "<dict>"] [(-s|--sources) Twitter]
    [(-m|--media) (image|sound|text|video)]
    [(-k|--keyword) <str>]
    [(-q|--quantity) <int>]
    [(-l|--location) <longitude> <latitude> <radius> (km|mi)]
    [(-i|--interval) <since> <until>]
    [(-h|--help)]

See https://ogre.readthedocs.org/en/latest/ for more information.

"""

import argparse
import json
import os
from ogre import OGRe


def main():

    """Process arguments and invoke OGRe to fetch some data."""

    parser = argparse.ArgumentParser(description="OpenFusion GIS Retriever")
    parser.add_argument(
        "--keys",
        help="API keys",
        default=None
    )
    parser.add_argument(
        "-s", "--sources",
        help="public APIs to get content from (required)",
        action="append",
        required=True
    )
    parser.add_argument(
        "-m", "--media",
        help="content mediums to get",
        default=("image", "sound", "text", "video"),
        action="append"
    )
    parser.add_argument(
        "-k", "--keyword",
        help="term to search for",
        default=""
    )
    parser.add_argument(
        "-q", "--quantity",
        help="quantity of results to fetch",
        type=int,
        default=15
    )
    parser.add_argument(
        "-l", "--location",
        help="latitude, longitude, radius, and unit",
        default=None,
        nargs=4
    )
    parser.add_argument(
        "-i", "--interval",
        help="earliest and latest moments (POSIX timestamps)",
        default=None,
        nargs=2
    )
    args = parser.parse_args()

    if args.keys is not None:
        args.keys = json.loads(args.keys)
    else:
        args.keys = {
            "Twitter": {
                "consumer_key": os.environ.get("TWITTER_CONSUMER_KEY"),
                "access_token": os.environ.get("TWITTER_ACCESS_TOKEN")
            }
        }
    if args.location is not None:
        args.location[0] = float(args.location[0])
        args.location[1] = float(args.location[1])
        args.location[2] = float(args.location[2])
    if args.interval is not None:
        args.interval[0] = float(args.interval[0])
        args.interval[1] = float(args.interval[1])

    print json.dumps(
        OGRe(args.keys).fetch(
            sources=args.sources,
            media=args.media,
            keyword=args.keyword,
            quantity=args.quantity,
            location=args.location,
            interval=args.interval
        ),
        indent=4,
        separators=(",", ": ")
    )


if __name__ == "__main__":
    main()
