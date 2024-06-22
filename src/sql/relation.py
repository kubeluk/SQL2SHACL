from typing import List, Tuple
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword
from column import Column
from constraint import TableConstraint


class Relation:
    """TODO"""

    def __init__(
        self,
        rel_name: str,
        expressions: List[List[Token]],
    ):
        self.name = rel_name
        self.expressions = expressions
        self.columns, self.table_constraints = self._classify_expressions()

    def _classify_expressions(
        self,
    ) -> Tuple[List[Column], List[TableConstraint]]:
        """TODO"""

        column_constraints = []
        table_constraints = []

        for expression_ in self.expressions:
            first_tkn = expression_[0]
            first_tkn_name = str(first_tkn)
            other_tkns = expression_[1:]

            if first_tkn.match(Name, None):
                column_constraints.append(Column(self, first_tkn_name, other_tkns))

            if first_tkn.match(Keyword, None):
                table_constraints.append(
                    TableConstraint(self, first_tkn_name, other_tkns)
                )

        return column_constraints, table_constraints
