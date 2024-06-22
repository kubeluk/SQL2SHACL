from typing import List, Tuple
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword
from relation import Relation
from constraint import ForeignKey


class Column:

    def __init__(self, rel: Relation, col_name: str, expression: List[Token]):
        self.parent = rel
        self.name = col_name
        self.expression = expression
        self.dtype = str(expression[0])
        self.constraints = expression[1:]
        self.unique, self.not_null = self._set_column_properties()
        self.references = self._set_references()

    def _set_column_properties(self) -> Tuple[bool, bool]:
        unique = False
        not_null = False

        for tkn in self.constraints:
            if tkn.match(Keyword, "UNIQUE"):
                unique = True

            if tkn.match(Keyword, "NOT NULL"):
                not_null = True

            if tkn.match(Keyword, "PRIMARY KEY"):
                unique = True
                not_null = True

        return unique, not_null

    def _set_references(self) -> ForeignKey:
        """TODO"""

        referenced_rel_name = None
        referenced_col_name = None

        for idx, constraint_ in enumerate(self.constraints):
            if constraint_.match(Keyword, "REFERENCES"):
                referenced_rel_name = str(self.constraints[idx + 1])
                parenthesis_content = self.constraints[idx + 2 :]

                for tkn in parenthesis_content:
                    if tkn.match(Name, None):
                        referenced_col_name = str(tkn)

        if referenced_rel_name is None:
            return None

        else:
            return ForeignKey(
                self.parent.name,
                [self.name],
                referenced_rel_name,
                [referenced_col_name],
            )
