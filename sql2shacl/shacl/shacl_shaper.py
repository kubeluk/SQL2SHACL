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

import logging
from rdflib import Graph
from pathlib import Path
from .iri_builder import Builder
from .shacl_provider import (
    Node,
    MaxData,
    CrdData,
    UnqTuple,
    CrdProp,
    MaxProp,
    InvMaxProp,
    InvProp,
    Prop,
)
from ..sql.ddl import DDL
from ..sql.relation import Relation
from ..sql.column import Column
from ..sql.constraint import (
    Constraint,
    TableUnique,
    TablePrimaryKey,
    TableForeignKey,
    ColumnForeignKey,
)

logger = logging.getLogger(__name__)


class Shaper:
    """Does the Constraint Rewriting from SQL to SHACL

    See Thapa2021 [1] for more details.

    [1] http://urn.nb.no/URN:NBN:no-90764
    """

    def __init__(self, iri_builder: Builder, ddl_manager: DDL):
        self._shapes_graph = Graph()
        self._iri_builder = iri_builder
        self._ddl_manager = ddl_manager
        self._relations = ddl_manager.relations
        self._unq_component_added = False

    def _handle_unique_tab_constraint(self, tab_constraint: TableUnique) -> None:
        """TODO"""

        if len(tab_constraint.column_names) == 1:
            col = tab_constraint.relation.get_column_by_name(
                tab_constraint.column_names[0]
            )
            col.set_unique(True)

        else:
            # TODO: are groups of columns used for primary keys really covered
            # by the custom SHACL SPARQL constraint from the paper?
            # -> otherwise skip here if len(col_uris) > 1 and print warning
            rel_name = tab_constraint.relation_name
            col_uris = [
                self._iri_builder.build_attribute_iri(rel_name, col_name)
                for col_name in tab_constraint.column_names
            ]
            rel_uri = self._iri_builder.build_class_iri(rel_name)

            self._shapes_graph += UnqTuple.shape(rel_uri, *col_uris)
            self._ensure_unique_component()

    def _handle_primary_key_tab_constraint(
        self, tab_constraint: TablePrimaryKey
    ) -> None:
        """Set all columns of primary key not null"""

        for col_name in tab_constraint.column_names:
            col = tab_constraint.relation.get_column_by_name(col_name)
            col.set_not_null(True)

    def _handle_foreign_key_tab_constraint(
        self, tab_constraint: TableForeignKey
    ) -> None:
        """TODO"""

        rel_name = tab_constraint.relation_name
        col_names = tab_constraint.column_names

        if len(col_names) > 1:
            logger.warning(
                f"Foreign keys that constrain and reference a group of columns (<{col_names}>) are not supported yet"
            )
            return

        rel_uri = self._iri_builder.build_class_iri(rel_name)
        referenced_rel_uri = self._iri_builder.build_class_iri(
            tab_constraint.referenced_relation_name
        )
        path_obj_uri = self._iri_builder.build_foreign_key_iri(
            rel_name,
            tab_constraint.referenced_relation_name,
            col_names,
            tab_constraint.referenced_column_names,
        )

        if tab_constraint.is_not_null:
            self._shapes_graph += CrdProp.shape(
                rel_uri, path_obj_uri, referenced_rel_uri
            )
        else:
            self._shapes_graph += MaxProp.shape(
                rel_uri, path_obj_uri, referenced_rel_uri
            )

        if tab_constraint.is_unique:
            self._shapes_graph += InvMaxProp.shape(
                referenced_rel_uri, path_obj_uri, rel_uri
            )
        else:
            self._shapes_graph += InvProp.shape(
                referenced_rel_uri, path_obj_uri, rel_uri
            )

    def _handle_table_constraint(self, tab_constraint: Constraint) -> None:
        """Handles expressions that start with a Token of ttype Keyword.

        This is the case for expressions that only define constraints, e.g.:
            PRIMARY KEY (ToEmp, ToPrj)
        """

        if isinstance(tab_constraint, TablePrimaryKey):
            self._handle_primary_key_tab_constraint(tab_constraint)
            self._handle_unique_tab_constraint(tab_constraint)

        elif isinstance(tab_constraint, TableUnique):
            self._handle_unique_tab_constraint(tab_constraint)

        elif isinstance(tab_constraint, TableForeignKey):
            self._handle_foreign_key_tab_constraint(tab_constraint)

        else:
            print(f"<{tab_constraint.name}> is not supported yet and will be skipped")

    def _handle_datatype_col_constraint(self, col: Column) -> None:
        """TODO"""

        rel = col.relation
        relation_name = rel.name
        col_name = col.name
        dtype_name = col.data_type

        rel_uri = self._iri_builder.build_class_iri(relation_name)
        attribute_uri = self._iri_builder.build_attribute_iri(relation_name, col_name)
        mapped_xmlschema_type_uri = self._iri_builder.build_datatype_iri(dtype_name)

        if col.has_not_null_constraint:
            self._shapes_graph += CrdData.shape(
                rel_uri, attribute_uri, mapped_xmlschema_type_uri
            )

        else:
            self._shapes_graph += MaxData.shape(
                rel_uri, attribute_uri, mapped_xmlschema_type_uri
            )

    def _ensure_unique_component(self) -> None:
        if not self._unq_component_added:
            unq_component = Graph().parse(
                Path("sql2shacl") / "components" / "unique_values_constraint.ttl",
                format="ttl",
            )
            self._shapes_graph += unq_component
            self._unq_component_added = True

    def _handle_unique_col_constraint(self, col: Column) -> None:
        """TODO"""

        if col.has_unique_constraint:
            rel_name = col.relation_name
            col_name = col.name

            self._shapes_graph += UnqTuple.shape(
                self._iri_builder.build_class_iri(rel_name),
                self._iri_builder.build_attribute_iri(rel_name, col_name),
            )
            self._ensure_unique_component()

    def _handle_references_col_constraint(self, col: Column) -> None:
        """TODO"""

        if isinstance(col.has_reference, ColumnForeignKey):
            ref = col.reference
            rel_uri = self._iri_builder.build_class_iri(col.relation_name)
            referenced_rel_uri = self._iri_builder.build_class_iri(
                ref.referenced_relation_name
            )
            path_obj_uri = self._iri_builder.build_foreign_key_iri(
                col.relation_name,
                ref.referenced_relation_name,
                [ref.column_name],
                [ref.referenced_column_name],
            )

            if col.has_not_null_constraint:
                self._shapes_graph += CrdProp.shape(
                    rel_uri, path_obj_uri, referenced_rel_uri
                )
            else:
                self._shapes_graph += MaxProp.shape(
                    rel_uri, path_obj_uri, referenced_rel_uri
                )

            if col.has_unique_constraint:
                self._shapes_graph += InvMaxProp.shape(
                    referenced_rel_uri, path_obj_uri, rel_uri
                )
            else:
                self._shapes_graph += InvProp.shape(
                    referenced_rel_uri, path_obj_uri, rel_uri
                )

    def _handle_column_constraint(self, col: Column) -> None:
        """TODO"""

        self._handle_datatype_col_constraint(col)
        self._handle_unique_col_constraint(col)
        self._handle_references_col_constraint(col)

    def _shape_relation(self, rel: Relation) -> None:
        """TODO"""

        logger.info(f"Shaping relation {rel.name} ...")
        node_shape = Node.shape(self._iri_builder.build_class_iri(rel.name))
        self._shapes_graph += node_shape

        # table constraints must be handled first
        for table_constraint in rel.table_constraints:
            self._handle_table_constraint(table_constraint)

        for column in rel.columns:
            self._handle_column_constraint(column)

    def _shape_binary_relation(self, rel: Relation) -> None:
        """Adds the respective shapes for binary relations.

        Since the relation is classified as binary, the `foreign_key_constraints` property
        either contains two `ColumnForeignKey` instances or one `TableForeignKey` instance.
        In the case of a `TableForeignKey`, both referenced columns come from the same referenced relation.
        """

        logger.info(f"Shaping binary relation {rel.name} ...")

        unique_properties = []
        ref_rel_names = []
        col_names = []
        ref_col_names = []

        # TODO: check if ref_col_names exist in ref_rel_names? (semantic check if foreign key is possible)
        for fk_constraint in rel.foreign_key_constraints:
            unique_properties.append(fk_constraint.is_unique)
            ref_rel_names.append(fk_constraint.referenced_relation_name)

            if isinstance(fk_constraint, ColumnForeignKey):
                col_names.append(fk_constraint.column_name)
                ref_col_names.append(fk_constraint.referenced_column_name)

            elif isinstance(fk_constraint, TableForeignKey):
                col_names.append(fk_constraint.column_names[0])
                ref_col_names.append(fk_constraint.referenced_column_names[0])

            else:
                logger.error(
                    f"""
                        Something went wrong.
                        Relation <{rel.name}> has been classified as binary,
                        but does not contain the right amount of foreign key constraints.
                    """
                )

        bin_rel_iri = self._iri_builder.build_foreign_key_iri_binary(
            rel.name,
            col_names[0],
            col_names[1],
            ref_col_names[0],
            ref_col_names[1],
        )
        ref_rel_1_iri = self._iri_builder.build_class_iri(ref_rel_names[0])
        ref_rel_2_iri = self._iri_builder.build_class_iri(ref_rel_names[1])

        if unique_properties[0]:
            self._shapes_graph += MaxProp.shape(
                ref_rel_1_iri, bin_rel_iri, ref_rel_2_iri
            )

        else:
            self._shapes_graph += Prop.shape(ref_rel_1_iri, bin_rel_iri, ref_rel_2_iri)

        if unique_properties[1]:
            self._shapes_graph += InvMaxProp.shape(
                ref_rel_2_iri, bin_rel_iri, ref_rel_1_iri
            )

        else:
            self._shapes_graph += InvProp.shape(
                ref_rel_2_iri, bin_rel_iri, ref_rel_1_iri
            )

    def shape_up(self) -> None:
        """Gets the output of DDLParser.parse_ddl() and builds SHACL shapes from it."""

        for relation_ in self._relations:
            if not self._ddl_manager.is_relation_binary(relation_):
                self._shape_relation(relation_)

            else:
                self._shape_binary_relation(relation_)

    def get_shapes(self) -> Graph:
        """TODO"""

        return self._shapes_graph
