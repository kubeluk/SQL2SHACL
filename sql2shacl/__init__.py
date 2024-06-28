"""Rewrite SQL constraints to SHACL shapes"""

import logging
import sql2shacl.constraint_rewriter as cr
from sql2shacl.utils import logging as cr_logging
from sql2shacl.utils import exceptions

__version__ = "v1.0.0"
__all__ = ["cr", "cr_logging", "exceptions"]


def rewrite(
    sql: str,
    base_iri: str = "http://example.org/base/",
    log_level: int = logging.WARNING,
    log_file: str = None,
) -> None:

    cr_logging.setup_logging(log_level, log_file)
    logger = logging.getLogger(__name__)

    try:
        rewriter = cr.ConstraintRewriter.setup(sql, base_iri)
        rewriter.rewrite()

    except exceptions.MissingSQLDatatypeException:
        logger.error("It seems there are missing data types in the column definitions")

    else:
        return rewriter.serialize_shapes()
