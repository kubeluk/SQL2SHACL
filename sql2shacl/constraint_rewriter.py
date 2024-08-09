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

import os
import logging
from typing import Dict, List
from pprint import pprint
from rdflib import Graph
from sqlparse.sql import Token
from .sql.ddl import DDL
from .shacl.shacl_shaper import Shaper
from .shacl.shacl_provider import UQ
from .shacl.iri_builder import Builder, SequedaBuilder, W3CBuilder

logger = logging.getLogger(__name__)


class ConstraintRewriter:

    def __init__(self, ddl_manager: DDL, iri_builder: Builder):
        self.ddl_manager = ddl_manager
        self.iri_builder = iri_builder
        self.shapes_graph = Graph()

    @classmethod
    def setup(
        cls,
        ddl_script: str,
        base_iri: str = "http://example.org/base/",
        mode: str = "w3c",
    ):
        if mode == "w3c":
            iri_builder = W3CBuilder(base_iri)

        elif mode == "sequeda":
            iri_builder = SequedaBuilder(base_iri)

        else:
            raise ValueError("Unknown IRI builder provided")

        logger.info("~~~ PARSING THE PROVIDED SQL SCRIPT ...")
        ddl_manager = DDL(ddl_script)

        return cls(ddl_manager, iri_builder)

    def get_parsed_ddl(self) -> Dict[str, List[List[Token]]]:
        """TODO"""

        return self.ddl_manager.relation_details

    def print_parsed_ddl(self) -> None:
        """TODO"""

        pprint(self.get_parsed_ddl())

    def rewrite(self) -> None:
        """TODO"""

        logger.info("~~~ REWRITING THE PARSED SQL CONSTRAINTS ...")
        shaper = Shaper(self.iri_builder, self.ddl_manager)
        shaper.shape_up()
        self.shapes_graph += shaper.get_shapes()

    def serialize_shapes(self) -> str:

        self.shapes_graph.bind("uq", UQ)
        return self.shapes_graph.serialize(format="ttl")
