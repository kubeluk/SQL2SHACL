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
import sqlparse
from typing import List, Dict, Tuple
from sqlparse.sql import Identifier, Parenthesis, Token, TokenList, Statement
from sqlparse.tokens import Name, Punctuation, Keyword, String, Comment
from .relation import Relation

# from .identifier import is_valid_identifier

logger = logging.getLogger(__name__)


class DDL:

    def __init__(self, ddl_script: str):
        self._parsed = sqlparse.parse(ddl_script)
        self._relation_details = self._break_down_statements()
        self._relations = self._break_down_relations()
        self._relations_dict = {rel.name: rel for rel in self._relations}

    @property
    def relation_details(self) -> Dict[str, List[List[Token]]]:
        """TODO"""

        return self._relation_details

    @property
    def relation_names(self) -> List[str]:
        """TODO"""

        return [rel_name for rel_name in self.relation_details.keys()]

    @property
    def relations(self) -> List[Relation]:
        """TODO"""

        return self._relations

    def is_other_relation_referencing(self, rel: Relation) -> bool:
        """TODO"""

        others = [other for other in self.relations if other.name != rel.name]

        for other_ in others:
            if rel.name in other_.referenced_relation_names:
                return True

        return False

    @staticmethod
    def _is_punctuation_end_of_expression(
        punct: Token, expression: List[Token]
    ) -> bool:
        """Returns if punctionation is the end of an expression.

        This is the case in every column definition but the last one, e.g.:
            ```
            CREATE TABLE Emp (
                E_id integer PRIMARY KEY,
                Name text NOT NULL,
                Post text
            )
            ```

        This is not the case when specifying table constraints, e.g.:
            ```
            CREATE TABLE Asg (
                ToEmp integer REFERENCES Emp (E_id),
                ToPrj integer REFERENCES Prj (P_id),
                PRIMARY KEY (ToEmp, ToPrj)
            )
            ```

        or:
            ```
            CREATE TABLE Projects (
                lead integer,
                name text,
                UNIQUE (lead, name),
                deptName text,
                deptCity text,
                UNIQUE (name, deptName, deptCity)
            )
            ```
        """

        punct_idx = expression.index(punct)
        next_tkn = expression[punct_idx + 1]
        next_next_tkn = expression[punct_idx + 2]

        if next_tkn.match(Name, None) or next_tkn.match(String.Symbol, None):
            if next_next_tkn.match(Punctuation, ",") or next_next_tkn.match(
                Punctuation, ")"
            ):
                return False

        return True

    @staticmethod
    def _is_end_of_parentesis_content(tkn: Token, tkn_list: List[Token]) -> bool:
        """Returns True if the token is the last element in the list."""

        return tkn_list.index(tkn) == (len(tkn_list) - 1)

    @staticmethod
    def _get_parenthesis_content(parenthesis_tkn: TokenList) -> List[Token]:
        """Returns the list of tokens with the starting and ending parentheses and 'Whitespace' removed."""

        content = list(parenthesis_tkn.flatten())[1:-1]
        return [tkn for tkn in content if not tkn.is_whitespace]

    def _is_create_table_statement(self, stmt: Statement) -> bool:
        if stmt.get_type() == "CREATE":
            for token in stmt.tokens:
                if token.match(Keyword, "TABLE"):
                    return True

        return False

    def _break_down_statement_(self, stmt: TokenList) -> Tuple[str, List[List[Token]]]:
        relation_name = None
        expressions = []

        for tkn in stmt.tokens:
            if isinstance(tkn, Identifier):
                relation_name = str(tkn)

            if isinstance(tkn, Parenthesis):
                content = DDL._get_parenthesis_content(tkn)
                expression_ = []

                for subtkn in content:
                    if subtkn.match(Comment.Single, None):
                        continue

                    if DDL._is_end_of_parentesis_content(subtkn, content):
                        expression_.append(subtkn)
                        expressions.append(expression_)
                        expression_ = []

                    elif subtkn.match(Punctuation, ","):
                        if DDL._is_punctuation_end_of_expression(subtkn, content):
                            expressions.append(expression_)
                            expression_ = []

                    else:
                        expression_.append(subtkn)

        return relation_name, expressions

    def _break_down_statements(self) -> Dict[str, List[List[Token]]]:
        """Parses table statements into table name and column expressions.

        ```
        <table definition> ::=
            CREATE [ <table scope> ] TABLE <table name> <table contents source>
            [ WITH <system versioning clause> ]
            [ ON COMMIT <table commit action> ROWS ]

        <identifier> ::=
            <actual identifier>

        <actual identifier> ::=
            <regular identifier>
            | <delimited identifier>
            | <Unicode delimited identifier>

        <regular identifier> ::=
            <identifier body>

        <identifier body> ::=
            <identifier start> [ <identifier part>... ]

        <identifier part> ::=
            <identifier start>
            | <identifier extend>

        <identifier start> ::=
            An <identifier start> is any character in the Unicode General Category
            classes “Lu”, “Ll”, “Lt”, “Lm”, “Lo”, or “Nl”

        <identifier extend> ::=
            An <identifier extend> is U+00B7, “Middle Dot”, or any character in the Unicode General Category
            classes “Mn”, “Mc”, “Nd”, or “Pc”

        <table scope> ::=
            <global or local> TEMPORARY

        <global or local> ::=
            GLOBAL
            | LOCAL

        <table contents source> ::=
            <table element list>

        <table element list> ::=
            <left paren> <table element> [ { <comma> <table element> }... ] <right paren>
        ```
        ---
        Token.Name:         column name
        Token.Name.Builtin: data type
        Token.Keyword:      constraint
        Token.Punctuation:  parenthesis
        """

        relation_details = {}

        for stmt in self._parsed:
            if not self._is_create_table_statement(stmt):
                logger.warning(
                    f"Skipping the following statement as it does not seem to be a DDL 'CREATE TABLE' statement: <{str(stmt)}>"
                )
                continue

            relation_name, expressions = self._break_down_statement_(stmt)

            # needed for official W3C test cases (using quotes is not valid SQL sytax)
            relation_name = relation_name.strip('"')
            #

            if relation_name is None:
                logger.warning(
                    f"Skipping the following statement since it does not contain a relation name: <{str(stmt)}>"
                )

            # elif not is_valid_identifier(relation_name):
            #     logger.warning(
            #         f"Skipping the following statement since <{relation_name}> is not a valid SQL identifier: <{str(stmt)}>"
            #     )

            else:
                relation_details[relation_name] = expressions

        return relation_details

    def _break_down_relations(self) -> List[Relation]:
        """TODO"""

        return [
            Relation(self, rel_name, expressions)
            for rel_name, expressions in self.relation_details.items()
        ]
