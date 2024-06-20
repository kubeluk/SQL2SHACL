from typing import Tuple
import sqlparse
from sqlparse.sql import Identifier, Parenthesis, Token, TokenList
from sqlparse.tokens import Name, Punctuation, Keyword
from typing import List, Dict


class TableParser:

    @staticmethod
    def _is_punctuation_end_of_expression(
        punct: Token, expression: List[Token]
    ) -> bool:
        """Returns if punctionation is the end of an expression.

        This is the case in every column definition but the last one, e.g.:
            CREATE TABLE Emp (
                E_id integer PRIMARY KEY,
                Name text NOT NULL,
                Post text
            );

        This is not the case when specifying key constraints, e.g.:
            CREATE TABLE Asg (
                ToEmp integer REFERENCES Emp (E_id),
                ToPrj integer REFERENCES Prj (P_id),
                PRIMARY KEY (ToEmp, ToPrj)
            );
        """

        punct_idx = expression.index(punct)
        tkn_before = expression[punct_idx - 1]
        tkn_after = expression[punct_idx + 1]

        # check if punctionation is surrounded by column names (= marks key constraint)
        if tkn_before.match(Name, None) and tkn_after.match(Name, None):
            return False

        return True

    @staticmethod
    def _is_last_tkn_in_list(tkn: Token, tkn_list: List[Token]) -> bool:
        """Returns True if the token is the last element in the list."""

        return tkn_list.index(tkn) == (len(tkn_list) - 1)

    @staticmethod
    def _get_parenthesis_subtkns(parenthesis_tkn: TokenList) -> List[Token]:
        """Returns the list of tokens with the starting and ending parentheses and 'Whitespace' removed."""

        content = list(parenthesis_tkn.flatten())[1:-1]
        return [tkn for tkn in content if not tkn.is_whitespace]

    @staticmethod
    def parse_ddl(ddl: str) -> Dict[str, List[List[Token]]]:
        """Parses SQL DDL constructing tables into a the respective columns, data types and constraints."""

        parsed = sqlparse.parse(ddl)
        relation_details = {}

        for stmt in parsed:
            relation_name = None
            expressions = []

            for tkn in stmt.tokens:
                if isinstance(tkn, Identifier):
                    relation_name = tkn.get_real_name()

                if isinstance(tkn, Parenthesis):
                    subtkns = TableParser._get_parenthesis_subtkns(tkn)
                    expression_ = []

                    for subtkn_ in subtkns:
                        if TableParser._is_last_tkn_in_list(subtkn_, subtkns):
                            expression_.append(subtkn_)
                            expressions.append(expression_)
                            expression_ = []

                        if subtkn_.match(Punctuation, ","):
                            if TableParser._is_punctuation_end_of_expression(
                                subtkn_, subtkns
                            ):
                                expressions.append(expression_)
                                expression_ = []
                                continue

                        expression_.append(subtkn_)

            relation_details[relation_name] = expressions

        return relation_details


class ConstraintParser:

    @staticmethod
    def parse_references_col_constraint(
        constraints: List[Token],
    ) -> Tuple[bool, bool, str, str]:
        """TODO"""

        not_null = False
        unique = False
        referenced_rel_name = None
        referenced_col_name = None

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

        return (
            not_null,
            unique,
            referenced_rel_name,
            referenced_col_name,
        )

    @staticmethod
    def parse_foreign_key_tab_constraint(
        constraint_params: List[Token],
    ) -> Tuple[bool, bool, List[str], str, List[str]]:
        """TODO"""

        not_null = False
        unique = False
        col_names = []
        referenced_rel_name = None
        referenced_col_names = []

        for idx, tkn in enumerate(constraint_params):
            if tkn.match(Keyword, "NOT NULL"):
                not_null = True

            if tkn.match(Keyword, "UNIQUE"):
                unique = True

            if tkn.match(Name, None):
                col_names.append(str(tkn))

            if tkn.match(Keyword, "REFERENCES"):
                referenced_rel_name = constraint_params[idx + 1]

                for ref in constraint_params[idx + 2 :]:
                    if ref.match(Name, None):
                        referenced_col_names.append(ref)

        return not_null, unique, col_names, referenced_rel_name, referenced_col_names
