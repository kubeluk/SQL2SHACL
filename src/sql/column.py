from typing import List, Tuple
from sqlparse.sql import Token
from sqlparse.tokens import Keyword
from .constraint import ColumnForeignKey


class Column:

    def __init__(self, parent, col_name: str, expression: List[Token]):
        self.parent = parent
        self.name = col_name
        self.expression = expression
        self.dtype = str(expression[0])
        self.constraints = expression[1:]
        self.unique, self.not_null, self.references = self._set_column_properties()

    def _set_column_properties(self) -> Tuple[bool, bool, ColumnForeignKey]:
        unique = False
        not_null = False
        references = None

        for idx, constraint_ in enumerate(self.constraints):
            if constraint_.match(Keyword, "UNIQUE"):
                unique = True

            if constraint_.match(Keyword, "NOT NULL"):
                not_null = True

            if constraint_.match(Keyword, "PRIMARY KEY"):
                unique = True
                not_null = True

            if constraint_.match(Keyword, "REFERENCES"):
                constraint_args = self.constraints[idx + 1 :]

                references = ColumnForeignKey(
                    self,
                    constraint_args,
                )

        return unique, not_null, references

    def get_name(self) -> str:
        """TODO"""

        return self.name

    def get_data_type(self) -> str:
        """TODO"""

        return self.dtype

    def has_unique_constraint(self) -> bool:
        """TODO"""

        return self.unique

    def has_not_null_constraint(self) -> bool:
        """TODO"""

        return self.not_null

    def has_references(self) -> bool:
        """TODO"""

        if self.references is None:
            return False

        return True

    def get_references(self) -> ColumnForeignKey:
        """TODO"""

        return self.references

    def get_relation_name(self) -> str:
        """TODO"""

        return self.parent.get_name()
