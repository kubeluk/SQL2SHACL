from typing import List, Tuple
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword
from relation import Relation


class ForeignKey:

    def __init__(
        self,
        rel: str,
        col_names: List[str],
        referenced_rel_name: str,
        referenced_col_names: List[str],
    ):
        self.parent = rel
        self.col_names = col_names
        self.referenced_rel_name = referenced_rel_name
        self.referenced_col_names = referenced_col_names


class TableConstraint:

    def __init__(self, rel: Relation, constraint_name: str, expression: List[Token]):
        self.parent = rel
        self.name = constraint_name
        self.expression = expression

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
