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
        return self.shapes_graph.serialize()

    def write_shapes(self, path: str) -> None:
        """TODO"""

        with open(path) as file:
            file.write(self.serialize_shapes())

    def print_shapes(self) -> str:
        """TODO"""

        print(self.serialize_shapes())
