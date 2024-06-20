from sql_parser import TableParser
from shacl_shaper import Shaper
from iri_builder import SequedaBuilder


class Rewriter:

    def __init__(self, ddl: str, base_uri: str = "http://to.do/"):
        self.ddl = ddl
        self.base_uri = base_uri

    def apply_constraint_rewriting(self):
        """Does the Constraint Rewriting from SQL to SHACL

        See Thapa2021 [1] for more details.

        [1] http://urn.nb.no/URN:NBN:no-90764
        """

        relation_details = TableParser.parse_ddl(self.ddl)
        iri_builder = SequedaBuilder(self.base_uri)
        shaper = Shaper(iri_builder, relation_details)
        self.shapes_graph = shaper.build_shapes()

        return self.shapes_graph


if __name__ == "__main__":
    DDL = """
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
    sg = Rewriter(DDL).apply_constraint_rewriting()
    print(sg.serialize())
