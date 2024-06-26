from typing import List, Tuple, Union, Dict
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword
from .column import Column
from .constraint import (
    Constraint,
    TableForeignKey,
    TablePrimaryKey,
    TableUnique,
    ColumnForeignKey,
)


class Relation:

    def __init__(
        self,
        rel_name: str,
        expressions: List[List[Token]],
    ):
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
    def foreign_key_column_constraints(self) -> List[Union[ColumnForeignKey, None]]:
        """TODO"""

        return [col.reference for col in self.columns if col.reference is not None]

    @property
    def foreign_key_table_constraints(self) -> List[Union[TableForeignKey, None]]:
        """TODO"""

        return [
            constraint
            for constraint in self.table_constraints
            if isinstance(constraint, TableForeignKey)
        ]

    @property
    def foreign_key_constraints(
        self,
    ) -> List[Union[Union[ColumnForeignKey, TableForeignKey], None]]:
        """TODO"""

        return self.foreign_key_column_constraints + self.foreign_key_table_constraints

    @property
    def referenced_relation_names(self) -> List[Union[str, None]]:
        """TODO"""

        return list(
            {
                constraint.referenced_relation_name
                for constraint in self.foreign_key_constraints
            }
        )

    @property
    def references_itself(self) -> bool:
        """TODO"""

        if self.name in self.referenced_relation_names:
            return True

        return False

    @property
    def primary_key_tab_constraint(self) -> Union[TablePrimaryKey, None]:
        """TODO"""

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

        if all([col.reference is not None for col in self.columns]):
            return True

        return False

    @property
    def do_all_columns_form_foreign_key(self) -> bool:
        """TODO"""

        for constraint in self.foreign_key_table_constraints:
            if constraint.column_names == self.column_names:
                return True

        return False

    def _prepare_foreign_key_references_per_column(
        self,
    ) -> Dict[str, List[Tuple[str, str]]]:
        """TODO"""

        foreign_key_refs = {}

        for constraint in self.foreign_key_constraints:
            ref_rel_name = constraint.referenced_relation_name

            if isinstance(constraint, ColumnForeignKey):
                col_name = constraint.column_name
                ref_col_name = constraint.referenced_column_name

            if isinstance(constraint, TableForeignKey):
                # only single-column foreign keys matter
                if len(constraint.column_names) == 1:
                    col_name = constraint.column_names[0]
                    ref_col_name = constraint.referenced_column_names[0]

                else:
                    continue

            refs = (ref_rel_name, ref_col_name)

            if foreign_key_refs.get(col_name, None) is None:
                foreign_key_refs[col_name] = [refs]

            else:
                foreign_key_refs[col_name].append(refs)

        return foreign_key_refs

    def _contains_duplicate_references_for_a_column(
        self, foreign_key_refs: dict
    ) -> bool:
        """TODO"""

        for _, refs in foreign_key_refs.items():
            ref_rels = [tup[0] for tup in refs]
            ref_cols = [tup[1] for tup in refs]

            if (len(ref_rels) != len(set(ref_rels))) or (
                len(ref_cols) != len(set(ref_cols))
            ):
                # col is referencing the same col of two distinct relations
                # or two distinct cols of the same relation
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
                    case "FOREIGN KEY":
                        tab_constraints.append(
                            TableForeignKey(self, constraint_name, constraint_args)
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
                        print(f"Skipping unknown constraint type <{constraint_type}>")

            else:
                print(
                    f"Skipping unknown table element, since <{first_tkn}> cannot be part of a valid SQL column or table constraint definition."
                )

        return cols, tab_constraints
