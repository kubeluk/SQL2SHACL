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
    mode: str = "w3c",
    log_level: int = logging.WARNING,
    log_file: str = None,
) -> str:

    cr_logging.setup_logging(log_level, log_file)
    logger = logging.getLogger(__name__)

    try:
        rewriter = cr.ConstraintRewriter.setup(sql, base_iri, mode)
        rewriter.rewrite()

    except exceptions.MissingSQLDatatypeException:
        logger.error("It seems there are missing data types in the column definitions")

    return rewriter.serialize_shapes()
