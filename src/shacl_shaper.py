from typing import List, Dict
from rdflib import Graph
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword
from table_classifier import is_relation_binary
from iri_builder import Builder, SequedaBuilder
from sql_parser import TableParser, ConstraintParser
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


class Shaper:

    def __init__(self, iri_builder: Builder, relation_details: Dict[str, List[Token]]):
        self.shapes_graph = Graph()
        self.iri_builder = iri_builder
        self.relation_details = relation_details
        self._unq_component_added = False

    def _handle_unique_tab_constraint(
        self, rel_name: str, parenthesis: List[Token]
    ) -> None:
        """TODO"""

        rel_uri = self.iri_builder.build_class_iri(rel_name)
        col_uris = [
            self.iri_builder.build_attribute_iri(rel_name, str(attr))
            for attr in parenthesis
            if attr.match(Name, None)
        ]

        self.shapes_graph += UnqTuple(rel_uri, *col_uris)

    def _handle_foreign_key_tab_constraint(
        self, rel_name: str, constraint_params: List[Token]
    ) -> None:
        """TODO"""

        not_null, unique, col_names, referenced_rel_name, referenced_col_names = (
            ConstraintParser.parse_foreign_key_tab_constraint(constraint_params)
        )

        if len(col_names) > 1:
            print(
                f"Foreign keys that constrain and reference a group of columns (<{col_names}>) are not supported yet"
            )

        self._handle_referenced_col(
            rel_name,
            col_names,
            referenced_rel_name,
            referenced_col_names,
            not_null,
            unique,
        )

    def _handle_table_constraint(self, rel_name: str, constraint: List[Token]) -> None:
        """Handles expressions that start with a Token of ttype Keyword.

        This is the case for expressions that only define constraints, e.g.:
            PRIMARY KEY (ToEmp, ToPrj)
        """

        constraint_name = str(constraint[0])
        constraint_params = constraint[1:]

        if (constraint_name == "UNIQUE") or (constraint_name == "PRIMARY KEY"):
            self._handle_unique_tab_constraint(rel_name, constraint_params)

        elif constraint_name == "FOREIGN KEY":
            self._handle_foreign_key_tab_constraint(rel_name, constraint_params)

        else:
            print(f"<{constraint_name}> is not supported yet and will be skipped")

    def _handle_datatype_col_constraint(
        self, rel_name: str, col_name: str, dtype_name: str, constraints: List[Token]
    ) -> None:
        """TODO"""

        rel_uri = self.iri_builder.build_class_iri(rel_name)
        attribute_uri = self.iri_builder.build_attribute_iri(rel_name, col_name)
        mapped_xmlschema_type_uri = self.iri_builder.build_datatype_iri(dtype_name)

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
                    self.iri_builder.build_class_iri(rel_name),
                    self.iri_builder.build_attribute_iri(rel_name, col_name),
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

        rel_uri = self.iri_builder.build_class_iri(rel_name)
        referenced_rel_uri = self.iri_builder.build_class_iri(referenced_rel_name)
        path_obj_uri = self.iri_builder.build_foreign_key_iri(
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

        not_null, unique, referenced_rel_name, referenced_col_name = (
            ConstraintParser.parse_references_col_constraint(constraints)
        )

        if referenced_col_name is None:
            return

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
                node_shape = Node(self.iri_builder.build_class_iri(rel_name))
                self.shapes_graph += node_shape

                # TODO: add logging which expressions haven't been handled
                for expression_ in expressions:
                    first_tkn = expression_[0]

                    if first_tkn.match(Name, None):
                        self._handle_column_constraint(rel_name, expression_)

                    if first_tkn.match(Keyword, None):
                        self._handle_table_constraint(rel_name, expression_)

            else:
                # TODO: handle binary relations
                pass

        return self.shapes_graph
