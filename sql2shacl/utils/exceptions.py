class MissingSQLDatatypeException(Exception):
    """Raised when column definition does not contain a data type."""

    pass


class UnsupportedSQLDatatypeException(Exception):
    """Raised when SQL datatype is not found in XSDSchema mapping file."""

    pass
