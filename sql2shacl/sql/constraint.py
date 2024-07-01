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
from typing import List, Tuple
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword

logger = logging.getLogger(__name__)


class Constraint:

    def __init__(self, parent, name: str, expression: List[Token]):
        self._parent = parent
        self._name = name
        self._expression = expression

    @property
    def name(self) -> str:
        """TODO"""

        return self._name

    @property
    def relation(self):
        """TODO"""

        return self._parent

    @property
    def relation_name(self) -> str:
        """TODO"""

        return self._parent.name

    def _break_down_expression(self):
        """
        ```
        <table constraint definition> ::=
            [ <constraint name definition> ] <table constraint>
            [ <constraint characteristics> ]

        <table constraint> ::=
            <unique constraint definition>
            | <referential constraint definition>
            | <check constraint definition>

        <unique constraint definition> ::=
            <unique specification> [ <unique null treatment> ]
            <left paren> <unique column list> [ <comma> <without overlap specification> ] <right paren>
            | UNIQUE <left paren> VALUE <right paren>

        <unique specification> ::=
            UNIQUE
            | PRIMARY KEY

        <unique column list> ::=
            <column name list>

        <referential constraint definition> ::=
            FOREIGN KEY <left paren> <referencing column list> [ <comma> <referencing period specification> ] <right paren>
            <references specification>

        <references specification> ::=
            REFERENCES <referenced table and columns>
            [ MATCH <match type> ] [ <referential triggered action> ]

        <referenced table and columns> ::=
            <table name> [ <left paren> <referenced column list> [ <comma> <referenced period specification> ] <right paren> ]
        """

        pass  # see child classes


class TableUnique(Constraint):

    def __init__(self, parent, name: str, expression: List[Token]):
        logger.info("with table constraint <UNIQUE>")
        super().__init__(parent, name, expression)
        self._col_names = self._break_down_expression()

    def _break_down_expression(self) -> List[str]:
        """TODO"""

        col_names = []
        for tkn in self._expression:
            if tkn.match(Name, None):
                col_names.append(str(tkn))

        return col_names

    @property
    def column_names(self) -> List[str]:
        """TODO"""

        return self._col_names


class TablePrimaryKey(TableUnique):

    def __init__(self, parent, name: str, expression: List[Token]):
        logger.info("with table constraint <PRIMARY KEY>")
        super().__init__(parent, name, expression)


class TableForeignKey(Constraint):

    def __init__(self, parent, name: str, expression: List[Token]):
        logger.info("with table constraint <FOREIGN KEY>")
        super().__init__(parent, name, expression)
        (
            self._unique,
            self._not_null,
            self._col_names,
            self._referenced_rel_name,
            self._referenced_col_names,
        ) = self._break_down_expression()

    def _break_down_expression(self) -> Tuple[bool, bool, List[str], str, List[str]]:
        """TODO"""

        unique = False
        not_null = False
        col_names = []
        referenced_rel_name = None
        referenced_col_names = []

        for idx, tkn in enumerate(self._expression):
            if tkn.match(Keyword, "UNIQUE"):
                unique = True

            if tkn.match(Keyword, "NOT NULL"):
                not_null = True

            if tkn.match(Name, None):
                col_names.append(str(tkn))

            if tkn.match(Keyword, "REFERENCES"):
                referenced_rel_name = self._expression[idx + 1]

                for ref in self._expression[idx + 2 :]:
                    if ref.match(Name, None):
                        referenced_col_names.append(ref)

        return not_null, unique, col_names, referenced_rel_name, referenced_col_names

    @property
    def column_names(self) -> List[str]:
        """TODO"""

        return self._col_names

    @property
    def referenced_relation_name(self) -> str:
        """TODO"""

        return self._referenced_rel_name

    @property
    def referenced_column_names(self) -> List[str]:
        """TODO"""

        return self._referenced_col_names

    @property
    def is_unique(self) -> bool:
        """TODO"""

        return self._unique

    @property
    def is_not_null(self) -> bool:
        """TODO"""

        return self._not_null


class ColumnForeignKey(Constraint):

    def __init__(self, parent, name: str, expression: List[Token]):
        logger.info("that has <REFERENCES> column constraint")
        super().__init__(parent, name, expression)
        self._col_name = parent.name
        self._referenced_rel_name, self._referenced_col_name = (
            self._break_down_expression()
        )

    def _break_down_expression(self) -> None:
        """TODO

        ---
        These two expressions are equal:
        ```
        CREATE TABLE orders (
            order_id integer PRIMARY KEY,
            product_no integer REFERENCES products (product_no),
            quantity integer
        )

        CREATE TABLE orders (
            order_id integer PRIMARY KEY,
            product_no integer REFERENCES products,
            quantity integer
        )
        ```
        """
        referenced_rel_name = str(self._expression[0])

        if len(self._expression) == 1:
            referenced_col_name = self._col_name

        else:
            parenthesis_content = self._expression[1:]

            for tkn in parenthesis_content:
                if tkn.match(Name, None):
                    referenced_col_name = str(tkn)
                    break

        return referenced_rel_name, referenced_col_name

    @property
    def column_name(self) -> str:
        return self._col_name

    @property
    def referenced_relation_name(self) -> str:
        return self._referenced_rel_name

    @property
    def referenced_column_name(self) -> str:
        return self._referenced_col_name

    @property
    def is_unique(self) -> bool:
        """TODO"""

        return self._parent.has_unique_constraint
