from typing import List, Tuple
from sqlparse.sql import Token
from sqlparse.tokens import Keyword, Name
from src.utils.exceptions import MissingSQLDatatypeException
from .constraint import ColumnForeignKey


class Column:
    """
    ```
    <column definition> ::=
        <column name> [ <data type or domain name> ]
        [ <default clause> | <identity column specification> | <generation clause>
        | <system time period start column specification>
        | <system time period end column specification> ]
        [ <column constraint definition>... ]
        [ <collate clause> ]

    <column constraint definition> ::=
        [ <constraint name definition> ] <column constraint> [ <constraint characteristics> ]

    <column constraint> ::=
        NOT NULL
        | <unique specification>
        | <references specification>
        | <check constraint definition>
    ```
    """

    def __init__(self, parent, col_name: str, expression: List[Token]):
        self._parent = parent
        self._name = col_name
        self._expression = expression
        self._dtype, self._unique, self._not_null, self._reference = (
            self._set_column_properties()
        )

    def _set_column_properties(self) -> Tuple[str, bool, bool, ColumnForeignKey]:
        if self._expression[0].match(Name.Builtin, None):
            dtype = str(self._expression[0])

        else:
            raise MissingSQLDatatypeException(
                f"Column <{self._name}> of relation <{self._parent.name}>"
            )

        unique = False
        not_null = False
        reference = None

        constraints = self._expression[1:]
        for idx, constraint_ in enumerate(constraints):
            if constraint_.match(Keyword, "UNIQUE"):
                unique = True

            if constraint_.match(Keyword, "NOT NULL"):
                not_null = True

            if constraint_.match(Keyword, "PRIMARY KEY"):
                unique = True
                not_null = True

            if constraint_.match(Keyword, "REFERENCES"):
                constraint_args = constraints[idx + 1 :]

                reference = ColumnForeignKey(
                    self,
                    constraint_args,
                )

        return dtype, unique, not_null, reference

    @property
    def name(self) -> str:
        """TODO"""

        return self._name

    @property
    def data_type(self) -> str:
        """TODO"""

        return self._dtype

    @property
    def has_unique_constraint(self) -> bool:
        """TODO"""

        return self._unique

    @property
    def has_not_null_constraint(self) -> bool:
        """TODO"""

        return self._not_null

    @property
    def has_reference(self) -> bool:
        """TODO"""

        if self._reference is None:
            return False

        return True

    @property
    def reference(self) -> ColumnForeignKey:
        """TODO"""

        return self._reference

    @property
    def relation_name(self) -> str:
        """TODO"""

        return self._parent.name
