from typing import List, Tuple
from sqlparse.sql import Token
from sqlparse.tokens import Keyword, Name
from utils.exceptions import MissingSQLDatatypeException
from .constraint import ColumnForeignKey


class Column:

    def __init__(self, parent, col_name: str, expression: List[Token]):
        self._parent = parent
        self._name = col_name
        self._expression = expression
        self._dtype, self._unique, self._not_null, self._reference = (
            self._set_column_properties()
        )

    def _set_column_properties(self) -> Tuple[str, bool, bool, ColumnForeignKey]:
        """
        ```
        <column definition> ::=
            <column name> [ <data type or domain name> ]
            [ <default clause> | <identity column specification> | <generation clause>
            | <system time period start column specification>
            | <system time period end column specification> ]
            [ <column constraint definition>... ]
            [ <collate clause> ]

        <data type> ::=
            <predefined type>
            | <row type>
            | <path-resolved user-defined type name>
            | <reference type>
            | <collection type>

        <predefined type> ::=
            <character string type> [ CHARACTER SET <character set specification> ] [ <collate clause> ]
            | <national character string type> [ <collate clause> ]
            | <binary string type>
            | <numeric type>
            | <boolean type>
            | <datetime type>
            | <interval type>
            | <JSON type>

        <character string type> ::=
            CHARACTER [ <left paren> <character length> <right paren> ]
            | CHAR [ <left paren> <character length> <right paren> ]
            | CHARACTER VARYING [ <left paren> <character maximum length> <right paren> ]
            | CHAR VARYING [ <left paren> <character maximum length> <right paren> ]
            | VARCHAR [ <left paren> <character maximum length> <right paren> ]
            | <character large object type>

        <character large object type> ::=
            CHARACTER LARGE OBJECT [ <left paren> <character large object length> <right paren> ]
            | CHAR LARGE OBJECT [ <left paren> <character large object length> <right paren> ]
            | CLOB [ <left paren> <character large object length> <right paren> ]

        <binary string type> ::=
            BINARY [ <left paren> <length> <right paren> ]
            | BINARY VARYING [ <left paren> <maximum length> <right paren> ]
            | VARBINARY [ <left paren> <maximum length> <right paren> ]
            | <binary large object string type>

        <binary large object string type> ::=
            BINARY LARGE OBJECT [ <left paren> <large object length> <right paren> ]
            | BLOB [ <left paren> <large object length> <right paren> ]

        <numeric type> ::=
            <exact numeric type>
            | <approximate numeric type>
            | <decimal floating-point type>

        <exact numeric type> ::=
            NUMERIC [ <left paren> <precision> [ <comma> <scale> ] <right paren> ]
            | DECIMAL [ <left paren> <precision> [ <comma> <scale> ] <right paren> ]
            | DEC [ <left paren> <precision> [ <comma> <scale> ] <right paren> ]
            | SMALLINT
            | INTEGER
            | INT
            | BIGINT

        <approximate numeric type> ::=
            FLOAT [ <left paren> <precision> <right paren> ]
            | REAL
            | DOUBLE PRECISION

        <decimal floating-point type> ::=
            DECFLOAT [ <left paren> <precision> <right paren> ]

        <boolean type> ::=
            BOOLEAN

        <datetime type> ::=
            DATE
            | TIME [ <left paren> <time precision> <right paren> ] [ <with or without time zone> ]
            | TIMESTAMP [ <left paren> <timestamp precision> <right paren> ]
            [ <with or without time zone> ]

        <interval type> ::=
            INTERVAL <interval qualifier>

        <JSON type> ::=
            JSON

        <column constraint definition> ::=
            [ <constraint name definition> ] <column constraint> [ <constraint characteristics> ]

        <column constraint> ::=
            NOT NULL
            | <unique specification>
            | <references specification>
            | <check constraint definition>
        ```
        """

        dtype = None
        unique = False
        not_null = False
        reference = None

        for idx, constraint_ in enumerate(self._expression):
            if constraint_.match(Name.Builtin, None):
                dtype = str(constraint_)

            if constraint_.match(Keyword, "UNIQUE"):
                unique = True

            if constraint_.match(Keyword, "NOT NULL"):
                not_null = True

            if constraint_.match(Keyword, "PRIMARY KEY"):
                unique = True
                not_null = True

            if constraint_.match(Keyword, "REFERENCES"):
                constraint_args = self._expression[idx + 1 :]

                reference = ColumnForeignKey(
                    self,
                    "",
                    constraint_args,
                )

        if dtype is None:
            raise MissingSQLDatatypeException(
                f"For column <{self._name}> of relation <{self._parent.name}>"
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
