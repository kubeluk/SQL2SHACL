"""
Copyright 2024 Lukas Kubelka and Xuemin Duan

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

import sql2shacl
import sys
import argparse
import logging
from io import TextIOWrapper


def create_parser():
    parser = argparse.ArgumentParser(
        prog="sql2shacl",
        description="Rewrite SQL constraints in FILE according to OPTIONS",
        usage="%(prog)s  [OPTIONS] FILE, ...",
    )

    parser.add_argument("filename")

    parser.add_argument(
        "--base-iri",
        dest="iri",
        metavar="IRI",
        default="http://example.org/base/",
        help="used as the IRI prefix (defaults to 'http://example.org/base/')",
    )

    parser.add_argument(
        "--mode",
        dest="mode",
        metavar="MODE",
        default="w3c",
        choices=["w3c", "thapa"],
        help="direct mapping assumptions based on which shacl shapes are generated (defaults to 'w3c)",
    )

    parser.add_argument(
        "-o",
        "--outfile",
        dest="outfile",
        metavar="OUTFILE",
        help="write output to OUTFILE (defaults to stdout)",
    )

    parser.add_argument(
        "--loglevel",
        dest="loglevel",
        metavar="LOGLEVEL",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="set loglevel (defaults to logging.WARNING)",
    )

    parser.add_argument("--version", action="version", version=sql2shacl.__version__)

    return parser


def _error(msg):
    """Print msg and optionally exit with return code exit_."""

    sys.stderr.write("[ERROR] {}\n".format(msg))

    return 1


def main(args=None):
    parser = create_parser()
    args = parser.parse_args(args)

    if args.filename == "-":  # read from stdin
        wrapper = TextIOWrapper(sys.stdin.buffer)
        try:
            data = wrapper.read()
        finally:
            wrapper.detach()

    else:
        try:
            with open(args.filename) as f:
                data = "".join(f.readlines())
        except OSError as e:
            return _error(f"Failed to read {args.filename}: {e}")

    loglevel = None
    if args.loglevel:
        match args.loglevel:
            case "DEBUG":
                loglevel = logging.DEBUG
            case "INFO":
                loglevel = logging.INFO
            case "WARNING":
                loglevel = logging.WARNING
            case "ERROR":
                loglevel = logging.ERROR
    else:
        loglevel = logging.WARNING

    # if args.iri:
    #     baseiri = args.iri
    # else:
    #     baseiri = "http://example.org/base/"

    close_stream = False
    if args.outfile:
        try:
            stream = open(args.outfile, "w", encoding="utf-8")
            close_stream = True
        except OSError as e:
            return _error(f"Failed to open {args.outfile}: {e}")

    else:
        stream = sys.stdout

    shapes_graph = sql2shacl.rewrite(sql=data, base_iri=args.iri, mode=args.mode, log_level=loglevel)

    stream.write(shapes_graph)
    stream.flush()

    if close_stream:
        stream.close()

    return 0
