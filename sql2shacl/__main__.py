"""Entrypoint module for `python -m sqlparse`."""

import sys
from sql2shacl.cli import main

if __name__ == "__main__":
    sys.exit(main())
