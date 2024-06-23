from typing import Dict, List
from pprint import pprint
from rdflib import Graph
from sqlparse.sql import Token
from sql.ddl import DDL
from shacl_shaper import Shaper
from iri_builder import Builder, SequedaBuilder


class ConstraintRewriter:

    def __init__(self, ddl_manager: DDL, iri_builder: Builder):
        self.ddl_manager = ddl_manager
        self.iri_builder = iri_builder
        self.shapes_graph = Graph()

    @classmethod
    def setup(
        cls,
        ddl_script: str,
        base_iri: str = "http://to.do/",
        iri_builder: str = "Sequeda",
    ):
        try:
            ddl_manager = DDL(ddl_script)
        except Exception:
            raise Exception("The provided DDL file could not be parsed properly")

        if iri_builder == "Sequeda":
            iri_builder = SequedaBuilder(base_iri)
        else:
            raise ValueError("Unknown IRI builder provided")

        return cls(ddl_manager, iri_builder)

    def get_parsed_ddl(self) -> Dict[str, List[List[Token]]]:
        """TODO"""

        return self.ddl_manager.get_relation_details()

    def print_parsed_ddl(self) -> None:
        """TODO"""

        pprint(self.get_parsed_ddl())

    def rewrite(self):
        """TODO"""

        shaper = Shaper(self.iri_builder, self.ddl_manager)
        shaper.shape_up()
        self.shapes_graph += shaper.get_shapes()

    def serialize_shapes(self) -> str:
        """TODO"""

        return self.shapes_graph.serialize()

    def print_shapes(self) -> str:
        """TODO"""

        print(self.serialize_shapes())


if __name__ == "__main__":
    ddl_script = """
        CREATE TABLE Emp (
            E_id integer PRIMARY KEY,
            Name char CONSTRAINT test_constraint NOT NULL,
            Post char
        );
        CREATE TABLE Acc (
            A_id integer,
            Name char UNIQUE,
            PRIMARY KEY (A_id)
        );
        CREATE TABLE Prj (
            P_id integer PRIMARY KEY,
            Name char NOT NULL,
            ToAcc integer NOT NULL UNIQUE REFERENCES Acc (A_id)
        );
        CREATE TABLE Asg (
            ToEmp integer REFERENCES Emp (E_id),
            ToPrj integer REFERENCES Prj (P_id),
            PRIMARY KEY (ToEmp, ToPrj)
        );
    """
    cr = ConstraintRewriter.setup(ddl_script)
    cr.rewrite()

    cr.print_parsed_ddl()
    print("\n" + (80 * "#") + "\n")
    cr.print_shapes()
