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

from __future__ import annotations

import logging
from typing import List, Tuple, Union, Dict, TYPE_CHECKING
from collections import defaultdict
from itertools import chain
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword, String, Comment
from .column import Column
from .constraint import (
    Constraint,
    TableForeignKey,
    TablePrimaryKey,
    TableUnique,
    ColumnForeignKey,
)

if TYPE_CHECKING:
    from .ddl import DDL

logger = logging.getLogger(__name__)


class Relation:

    def __init__(
        self,
        rel_manager: DDL,
        rel_name: str,
        expressions: List[List[Token]],
    ):
        self._rel_manager = rel_manager
        logger.info(f"Identified relation <{rel_name}>")
        self._name = rel_name
        self._expressions = expressions
        self._cols, self._tab_constraints = self._classify_expressions()

    @property
    def name(self) -> str:
        """TODO"""

        return self._name

    @property
    def columns(self) -> List[Column]:
        """TODO"""

        return self._cols

    @property
    def table_constraints(self) -> List[Constraint]:
        """TODO"""

        return self._tab_constraints

    @property
    def n_columns(self) -> int:
        """TODO"""

        return len(self.columns)

    @property
    def column_names(self) -> List[str]:
        """TODO"""

        return [col.name for col in self.columns]

    @property
    def references_column_constraints(self) -> List[ColumnForeignKey]:
        """TODO"""

        return [col.reference for col in self.columns if col.has_reference]

    @property
    def foreign_key_table_constraints(self) -> List[TableForeignKey]:
        """TODO"""

        return [
            constraint
            for constraint in self.table_constraints
            if isinstance(constraint, TableForeignKey)
        ]

    @property
    def referenced_relation_names(self) -> List[Union[str, None]]:
        """Returns a list of distinct referenced relation names."""

        return list(
            {
                constraint.referenced_relation_name
                for constraint in (
                    self.foreign_key_table_constraints
                    + self.references_column_constraints
                )
            }
        )

    @property
    def references_itself(self) -> bool:
        """Returns whether the relation's name is referenced in an own constraint."""

        if self.name in self.referenced_relation_names:
            return True

        return False

    @property
    def primary_key_tab_constraint(self) -> Union[TablePrimaryKey, None]:
        """Returns the `PRIMARY KEY` table constraint if existing."""

        for constraint in self.table_constraints:
            if isinstance(constraint, TablePrimaryKey):
                return constraint

        return None

    @property
    def has_exactly_two_attributes(self) -> bool:
        """TODO"""

        if self.n_columns == 2:
            return True

        return False

    @property
    def do_all_columns_form_primary_key(self) -> bool:
        """TODO"""

        if self.primary_key_tab_constraint is not None:
            if self.primary_key_tab_constraint.column_names == self.column_names:
                return True

        return False

    @property
    def do_all_columns_reference(self) -> bool:
        """TODO"""

        referencing_table_constraint_column_names = list(
            chain(
                *[
                    constraint.column_names
                    for constraint in self.foreign_key_table_constraints
                ]
            )
        )

        referencing_column_constraint_column_names = [
            col.name for col in self.columns if col.has_reference
        ]

        all_referencing_column_names = (
            referencing_table_constraint_column_names
            + referencing_column_constraint_column_names
        )

        if set(all_referencing_column_names) == set(self.column_names):
            return True

        return False

    @property
    def do_all_columns_form_foreign_key(self) -> bool:
        """TODO"""

        for constraint in self.foreign_key_table_constraints:
            if constraint.column_names == self.column_names:
                return True

        return False

    def get_column_by_name(self, col_name: str) -> Column:
        """TODO"""

        for col in self.columns:
            if col.name == col_name:
                return col

        return None

    def _prepare_foreign_key_references_per_column(
        self,
    ) -> Dict[str, List[Tuple[str, str]]]:
        """Returns a dict containing for each referencing column the respective referenced column and referenced relation name

        Wrt `TableForeignKey`, only single-column foreign keys matter here,
        bc this method is only used for checking whether a relation is binary."""

        foreign_key_refs = defaultdict(list)
        foreign_key_constraints = (
            self.references_column_constraints + self.foreign_key_table_constraints
        )

        for constraint in foreign_key_constraints:
            ref_rel_name = constraint.referenced_relation_name

            if isinstance(constraint, ColumnForeignKey):
                col_name = constraint.column_name
                ref_col_name = constraint.referenced_column_name

            if isinstance(constraint, TableForeignKey):
                if len(constraint.column_names) == 1:
                    col_name = constraint.column_names[0]
                    ref_col_name = constraint.referenced_column_names[0]

                else:
                    continue

            refs = (ref_rel_name, ref_col_name)
            foreign_key_refs[col_name].append(refs)

        return foreign_key_refs

    def _contains_duplicate_references_for_a_column(
        self, foreign_key_refs: dict
    ) -> bool:
        """Returns whether a column is the attribute of two distinct foreign keys

        This is the case when a column is referencing the same column of two distinct relations
        or two distinct columns of the same relation."""

        for _, refs in foreign_key_refs.items():
            ref_rels = [tup[0] for tup in refs]
            ref_cols = [tup[1] for tup in refs]

            if (len(ref_rels) != len(set(ref_rels))) or (
                len(ref_cols) != len(set(ref_cols))
            ):
                return True

        return False

    def has_column_involved_in_two_distinct_foreign_keys(self) -> bool:
        """Returns whether an attribute of the relation is the attribute
        of two distinct foreign keys in the relation.

        For that see if a column name appears multiple times in a constraint
        and references distinct other column names.
        ---
        ```
        TWOFK(X, Y) ← FK_1(X, Y, U1, V1), FK_1(X, Y, U2, V2), U1 != U2
        TWOFK(X, Y) ← FK_1(X, Y, U1, V1), FK_1(X, Y, U2, V2), V1 != V2
        ```
        """

        return self._contains_duplicate_references_for_a_column(
            self._prepare_foreign_key_references_per_column()
        )

    def is_binary(self) -> bool:
        """Returns if a relation is a binary relation

        Informally, a relation R is a binary relation between two relations S and T if:

            1. both S and T are different from R
            2. R has exactly two attributes A and B, which form a primary key of R
            3. A is the attribute of a foreign key in R that points to S
            4. B is the attribute of a foreign key in R that points to T
            5. A is not the attribute of two distinct foreign keys in R
            6. B is not the attribute of two distinct foreign keys in R
            7. A and B are not the attributes of a composite foreign key in R
            8. relation R does not have incoming foreign keys

        See Sequeda2012 [1] for details.

        Example for a binary relation:
        ```
        CREATE TABLE Asg (
            ToEmp integer REFERENCES Emp (E_id),
            ToPrj integer REFERENCES Prj (P_id),
            PRIMARY KEY (ToEmp, ToPrj)
        )
        ```

        [1] https://doi.org/10.1145/2187836.2187924
        """

        if (
            not self.references_itself  # 1 (in combination with 2)
            and self.has_exactly_two_attributes  # 2
            and self.do_all_columns_form_primary_key  # 2
            and self.do_all_columns_reference  # 3, 4 (in combination with 2)
            and not self.has_column_involved_in_two_distinct_foreign_keys()  # 5, 6
            and not self.do_all_columns_form_foreign_key  # 7
            and not self._rel_manager.is_other_relation_referencing(self)  # 8
        ):
            return True

        return False

    def _classify_expressions(
        self,
    ) -> Tuple[List[Column], List[Constraint]]:
        """
        ```
        <table element list> ::=
            <left paren> <table element> [ { <comma> <table element> }... ] <right paren>

        <table element> ::=
            <column definition>
            | <table period definition>
            | <table constraint definition>
            | <like clause>

        <column definition> ::=
            <column name> [ <data type or domain name> ]
            [ <default clause> | <identity column specification> | <generation clause>
            | <system time period start column specification>
            | <system time period end column specification> ]
            [ <column constraint definition>... ]
            [ <collate clause> ]

        <table period definition> ::=
            <system or application time period specification>
            <left paren> <period begin column name> <comma> <period end column name> <right paren>

        <system or application time period specification> ::=
            <system time period specification>
            | <application time period specification>

        <system time period specification> ::=
            PERIOD FOR SYSTEM_TIME

        <table constraint definition> ::=
            [ <constraint name definition> ] <table constraint>
            [ <constraint characteristics> ]

        <constraint name definition> ::=
            CONSTRAINT <constraint name>

        <table constraint> ::=
            <unique constraint definition>
            | <referential constraint definition>
            | <check constraint definition>

        <like clause> ::=
            LIKE <table name> [ <like options> ]
        ```
        """

        cols = []
        tab_constraints = []

        for expression_ in self._expressions:
            first_tkn = expression_[0]
            other_tkns = expression_[1:]

            if first_tkn.match(Name, None):
                col_name = str(first_tkn)
                cols.append(Column(self, col_name, other_tkns))

            # needed for W3C RDB2RDF test cases (using quotes is not valid SQL syntax)
            elif first_tkn.match(String.Symbol, None):
                col_name = str(first_tkn).strip('"')
                cols.append(Column(self, col_name, other_tkns))
            #

            elif first_tkn.match(Keyword, None):
                if str(first_tkn) == "CONSTRAINT":
                    constraint_name = str(other_tkns[0])
                    constraint_type = str(other_tkns[1])
                    constraint_args = other_tkns[2:]

                else:
                    constraint_name = ""
                    constraint_type = str(first_tkn)
                    constraint_args = other_tkns

                match constraint_type:
                    # sqlparse 0.5.0 does not recognize 'FOREIGN KEY' as one Keyword, rather 'FOREIGN' and 'KEY' separately
                    case "FOREIGN":
                        tab_constraints.append(
                            TableForeignKey(
                                self,
                                constraint_name,
                                constraint_args[
                                    1:
                                ],  # skip 'KEY' keyword in constraint_args
                            )
                        )

                    case "PRIMARY KEY":
                        tab_constraints.append(
                            TablePrimaryKey(self, constraint_name, constraint_args)
                        )

                    case "UNIQUE":
                        tab_constraints.append(
                            TableUnique(self, constraint_name, constraint_args)
                        )

                    case _:
                        logger.warning(
                            f"Skipping unsupported keyword <{constraint_type}>"
                        )

            elif first_tkn.match(Comment.Single, None):
                pass

            else:
                logger.warning(
                    f"Skipping unknown table element <{first_tkn}>, since it cannot be part of a valid SQL column or table constraint definition."
                )

        return cols, tab_constraints
