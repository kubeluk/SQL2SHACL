from typing import List
from rdflib import Graph
from sqlparse.sql import Token
from iri_builder import Builder
from sql.ddl import DDL
from sql.relation import Relation
from sql.column import Column
from sql.constraint import (
    Constraint,
    TableUnique,
    TableForeignKey,
)
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
    """Does the Constraint Rewriting from SQL to SHACL

    See Thapa2021 [1] for more details.

    [1] http://urn.nb.no/URN:NBN:no-90764
    """

    def __init__(self, iri_builder: Builder, ddl_manager: DDL):
        self.shapes_graph = Graph()
        self.iri_builder = iri_builder
        self.ddl_manager = ddl_manager
        self.relations = ddl_manager.get_relations()
        self._unq_component_added = False

    def _handle_unique_tab_constraint(self, tab_constraint: TableUnique) -> None:
        """TODO"""

        rel_name = tab_constraint.get_relation_name()
        rel_uri = self.iri_builder.build_class_iri(rel_name)
        # TODO: are groups of columns used for primary keys really covered
        # by the custom SHACL SPARQL constraint from the paper?
        # -> otherwise skip here if len(col_uris) > 1 and print warning
        col_uris = [
            self.iri_builder.build_attribute_iri(rel_name, col_name)
            for col_name in tab_constraint.get_col_names()
        ]

        self.shapes_graph += UnqTuple(rel_uri, *col_uris)

    def _handle_foreign_key_tab_constraint(
        self, tab_constraint: TableForeignKey
    ) -> None:
        """TODO"""

        rel_name = tab_constraint.get_relation_name()
        col_names = tab_constraint.get_column_names()

        if len(col_names) > 1:
            print(
                f"Foreign keys that constrain and reference a group of columns (<{col_names}>) are not supported yet"
            )
            return

        referenced_rel_name = tab_constraint.get_referenced_relation_name()
        referenced_col_names = tab_constraint.get_referenced_col_names()
        rel_uri = self.iri_builder.build_class_iri(rel_name)
        referenced_rel_uri = self.iri_builder.build_class_iri(referenced_rel_name)
        path_obj_uri = self.iri_builder.build_foreign_key_iri(
            rel_name, referenced_rel_name, col_names, referenced_col_names
        )

        if tab_constraint.is_not_null():
            self.shapes_graph += CrdProp(rel_uri, path_obj_uri, referenced_rel_uri)
        else:
            self.shapes_graph += MaxProp(rel_uri, path_obj_uri, referenced_rel_uri)

        if tab_constraint.is_unique():
            self.shapes_graph += InvMaxProp(referenced_rel_uri, path_obj_uri, rel_uri)
        else:
            self.shapes_graph += InvProp(referenced_rel_uri, path_obj_uri, rel_uri)

    def _handle_table_constraint(self, tab_constraint: Constraint) -> None:
        """Handles expressions that start with a Token of ttype Keyword.

        This is the case for expressions that only define constraints, e.g.:
            PRIMARY KEY (ToEmp, ToPrj)
        """

        if isinstance(tab_constraint, TableUnique):
            self._handle_unique_tab_constraint(tab_constraint)

        elif isinstance(tab_constraint, TableForeignKey):
            self._handle_foreign_key_tab_constraint(tab_constraint)

        else:
            print(
                f"<{tab_constraint.get_constraint_name()}> is not supported yet and will be skipped"
            )

    def _handle_datatype_col_constraint(self, col: Column) -> None:
        """TODO"""

        relation_name = col.get_relation_name()
        col_name = col.get_name()
        dtype_name = col.get_data_type()

        rel_uri = self.iri_builder.build_class_iri(relation_name)
        attribute_uri = self.iri_builder.build_attribute_iri(relation_name, col_name)
        mapped_xmlschema_type_uri = self.iri_builder.build_datatype_iri(dtype_name)

        if col.has_unique_constraint():
            self.shapes_graph += CrdData(
                rel_uri, attribute_uri, mapped_xmlschema_type_uri
            )

        else:
            self.shapes_graph += MaxData(
                rel_uri, attribute_uri, mapped_xmlschema_type_uri
            )

    def _ensure_unique_component(self) -> None:
        if not self._unq_component_added:
            unq_component = Graph().parse(
                "src/components/unique_values_constraint.ttl", format="ttl"
            )
            self.shapes_graph += unq_component
            self._unq_component_added = True

    def _handle_unique_col_constraint(self, col: Column) -> None:
        """TODO"""

        if col.has_unique_constraint():
            rel_name = col.get_relation_name()
            col_name = col.get_name()

            self.shapes_graph += UnqTuple(
                self.iri_builder.build_class_iri(rel_name),
                self.iri_builder.build_attribute_iri(rel_name, col_name),
            )

            self._ensure_unique_component()

    def _handle_references_col_constraint(self, col: Column) -> None:
        """TODO"""

        if col.has_references():
            ref = col.get_references()
            rel_name = col.get_relation_name()
            referenced_rel_name = ref.get_referenced_rel_name()
            col_name = ref.get_col_name()
            referenced_col_name = ref.get_referenced_col_name()
            rel_uri = self.iri_builder.build_class_iri(rel_name)
            referenced_rel_uri = self.iri_builder.build_class_iri(referenced_rel_name)
            path_obj_uri = self.iri_builder.build_foreign_key_iri(
                rel_name, referenced_rel_name, [col_name], [referenced_col_name]
            )

            if col.has_not_null_constraint():
                self.shapes_graph += CrdProp(rel_uri, path_obj_uri, referenced_rel_uri)
            else:
                self.shapes_graph += MaxProp(rel_uri, path_obj_uri, referenced_rel_uri)

            if col.has_unique_constraint():
                self.shapes_graph += InvMaxProp(
                    referenced_rel_uri, path_obj_uri, rel_uri
                )
            else:
                self.shapes_graph += InvProp(referenced_rel_uri, path_obj_uri, rel_uri)

    def _handle_column_constraint(self, col: Column) -> None:
        """TODO"""

        self._handle_datatype_col_constraint(col)
        self._handle_unique_col_constraint(col)
        self._handle_references_col_constraint(col)

    def _shape_relation(self, rel: Relation) -> None:
        """TODO"""

        node_shape = Node(self.iri_builder.build_class_iri(rel.get_name()))
        self.shapes_graph += node_shape

        # TODO: add logging which expressions haven't been handled
        for column in rel.get_columns():
            self._handle_column_constraint(column)

        for table_constraint in rel.get_table_constraints():
            self._handle_table_constraint(table_constraint)

    def _shape_binary_relation(self, rel_name, expressions: List[List[Token]]) -> None:
        """TODO"""

        pass

    def shape_up(self) -> None:
        """Gets the output of DDLParser.parse_ddl() and builds SHACL shapes from it."""

        for relation_ in self.relations:
            if not self.ddl_manager.is_relation_binary(relation_.get_name()):
                self._shape_relation(relation_)

            else:
                self._shape_binary_relation(relation_)

    def get_shapes(self) -> Graph:
        """TODO"""

        return self.shapes_graph
