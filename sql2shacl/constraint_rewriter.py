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
from .shacl.iri_builder import Builder, SequedaBuilder

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
        iri_builder: str = "Sequeda",
    ):
        if iri_builder == "Sequeda":
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

    def rewrite(self):
        """TODO"""

        logger.info("~~~ REWRITING THE PARSED SQL CONSTRAINTS ...")
        shaper = Shaper(self.iri_builder, self.ddl_manager)
        shaper.shape_up()
        self.shapes_graph += shaper.get_shapes()

    def serialize_shapes(self) -> str:
        """TODO"""

        self.shapes_graph.bind("uq", UQ)
        return self.shapes_graph.serialize(format="ttl")

    def write_shapes(self, file_path: str) -> None:
        """TODO"""

        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "w") as file:
            file.write(self.serialize_shapes())

    def print_shapes(self) -> str:
        """TODO"""

        print(self.serialize_shapes())
