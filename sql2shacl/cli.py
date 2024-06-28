import sql2shacl
import sys
import argparse
import logging
from io import TextIOWrapper


def create_parser():
    parser = argparse.ArgumentParser(
        prog="sql2shacl",
        description='Rewrite SQL constraints in FILE according to OPTIONS. Use "-" as FILE '
        "to read from stdin.",
        usage="%(prog)s  [OPTIONS] FILE, ...",
    )

    parser.add_argument("filename")

    parser.add_argument(
        "--base-iri",
        dest="iri",
        metavar="IRI",
        help="used as the IRI prefix (defaults to 'http://example.org/')",
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

    if args.iri:
        baseiri = args.iri
    else:
        baseiri = "http://example.org/base/"

    close_stream = False
    if args.outfile:
        try:
            stream = open(args.outfile, "w")
            close_stream = True
        except OSError as e:
            return _error(f"Failed to open {args.outfile}: {e}")

    else:
        stream = sys.stdout

    shapes_graph = sql2shacl.rewrite(sql=data, base_iri=baseiri, log_level=loglevel)

    stream.write(shapes_graph)
    stream.flush()

    if close_stream:
        stream.close()

    return 0
