from typing import List, Dict
from rdflib import Graph
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword
from table_parser import parse_ddl
from shacl_provider import (
    Node,
    MaxData,
    CrdData,
    UnqTuple,
    CrdProp,
    MaxProp,
    InvMaxProp,
    InvProp,
)
from table_classifier import is_relation_binary
from iri_builder import (
    build_class_iri,
    build_attribute_iri,
    build_datatype_iri,
    build_foreign_key_iri,
    build_foreign_key_iri_binary,
)


class Shaper:

    def __init__(self, relation_details: Dict[str, List[Token]]):
        self.shapes_graph = Graph()
        self.relation_details = relation_details
        self._unq_component_added = False

    def _handle_table_constraint(self, expression: List[Token]) -> None:
        """Handles expressions that start with a Token of ttype Keyword.

        This is the case for expressions that only define constraints, e.g.:
            PRIMARY KEY (ToEmp, ToPrj)
        """

        constraint = expression[0]

        match constraint:
            case "PRIMARY KEY":
                pass
            case "FOREIGN KEY":
                pass
            case "UNIQUE":
                pass
            case _:
                # TODO: log unhandled constraint
                return

    def _handle_datatype_col_constraint(
        self, rel_name: str, col_name: str, dtype_name: str, constraints: List[Token]
    ) -> None:
        """TODO"""

        rel_uri = build_class_iri(rel_name)
        attribute_uri = build_attribute_iri(rel_name, col_name)
        mapped_xmlschema_type_uri = build_datatype_iri(dtype_name)

        for tkn in constraints:
            if tkn.match(Keyword, "NOT NULL") or tkn.match(Keyword, "PRIMARY KEY"):
                self.shapes_graph += CrdData(
                    rel_uri, attribute_uri, mapped_xmlschema_type_uri
                )
                return

        self.shapes_graph += MaxData(rel_uri, attribute_uri, mapped_xmlschema_type_uri)
        return

    def _ensure_unique_component(self) -> None:
        if not self._unq_component_added:
            unq_component = Graph().parse(
                "src/components/unique_values_constraint.ttl", format="ttl"
            )
            self.shapes_graph += unq_component
            self._unq_component_added = True

    def _handle_unique_col_constraint(
        self, rel_name: str, col_name: str, constraints: List[Token]
    ) -> None:
        """TODO"""

        for tkn in constraints:
            if tkn.match(Keyword, "UNIQUE") or tkn.match(Keyword, "PRIMARY KEY"):
                self.shapes_graph += UnqTuple(
                    build_class_iri(rel_name), build_attribute_iri(rel_name, col_name)
                )

            self._ensure_unique_component()

    def _handle_referenced_col(
        self,
        rel_name: str,
        col_name: str,
        referenced_rel_name: str,
        referenced_col_name: str,
        not_null: bool,
        unique: bool,
    ) -> None:
        """TODO"""

        rel_uri = build_class_iri(rel_name)
        referenced_rel_uri = build_class_iri(referenced_rel_name)
        path_obj_uri = build_foreign_key_iri(
            rel_name, referenced_rel_name, [col_name], [referenced_col_name]
        )

        if not_null:
            self.shapes_graph += CrdProp(rel_uri, path_obj_uri, referenced_rel_uri)
        else:
            self.shapes_graph += MaxProp(rel_uri, path_obj_uri, referenced_rel_uri)

        if unique:
            self.shapes_graph += InvMaxProp(referenced_rel_uri, path_obj_uri, rel_uri)
        else:
            self.shapes_graph += InvProp(referenced_rel_uri, path_obj_uri, rel_uri)

    def _handle_references_col_constraint(
        self, rel_name: str, col_name: str, constraints: List[Token]
    ) -> None:
        """TODO"""

        not_null = False
        unique = False

        for idx, constraint_ in enumerate(constraints):
            if constraint_.match(Keyword, "NOT NULL"):
                not_null = True

            if constraint_.match(Keyword, "UNIQUE"):
                unique = True

            if constraint_.match(Keyword, "REFERENCES"):
                referenced_rel_name = str(constraints[idx + 1])
                parenthesis_content = constraints[idx + 2 :]

                for tkn in parenthesis_content:
                    if tkn.match(Name, None):
                        referenced_col_name = str(tkn)
                        self._handle_referenced_col(
                            rel_name,
                            col_name,
                            referenced_rel_name,
                            referenced_col_name,
                            not_null,
                            unique,
                        )

    def _handle_column_constraint(self, rel_name: str, expression: List[Token]) -> None:
        """TODO"""

        col_name = str(expression[0])
        dtype_name = str(expression[1])
        constraints = expression[2:]

        self._handle_datatype_col_constraint(
            rel_name, col_name, dtype_name, constraints
        )
        self._handle_unique_col_constraint(rel_name, col_name, constraints)
        self._handle_references_col_constraint(rel_name, col_name, constraints)

    def build_shapes(self) -> Graph:
        """Gets the output of table_parser.parse_ddl() and builds SHACL shapes from it.

        Token.Name: column name
        Token.Name.Builtin: data type
        Token.Keyword: constraint
        Token.Punctuation: parenthesis
        """

        for rel_name, expressions in self.relation_details.items():
            if not is_relation_binary(
                expressions
            ):  # TODO: impelement is_relation_binary()
                node_shape = Node(build_class_iri(rel_name))
                self.shapes_graph += node_shape

                # TODO: add logging which expressions haven't been handled
                for expression_ in expressions:
                    first_tkn = expression_[0]

                    if first_tkn.match(Name, None):
                        self._handle_column_constraint(rel_name, expression_)

                    if first_tkn.match(Keyword, None):
                        self._handle_table_constraint(expression_)

            # else:
            #     pass  # TODO: handle binary relations

        return self.shapes_graph


if __name__ == "__main__":
    DDL = """
        CREATE TABLE Emp (
            E_id integer PRIMARY KEY,
            Name char CONSTRAINT test_constraint NOT NULL,
            Post char
        );
        CREATE TABLE Acc (
            A_id integer PRIMARY KEY,
            Name char UNIQUE
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

    relation_details = parse_ddl(DDL)
    shaper = Shaper(relation_details)
    shapes_graph = shaper.build_shapes()

    print(shapes_graph.serialize())
