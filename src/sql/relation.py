from typing import List, Tuple
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword
from .column import Column
from .constraint import Constraint, TableForeignKey, TablePrimaryKey, TableUnique


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

    def get_name(self) -> str:
        """TODO"""

        return self.name

    def get_columns(self) -> List[Column]:
        """TODO"""

        return self.columns

    def get_table_constraints(self) -> List[Constraint]:
        """TODO"""

        return self.table_constraints

    def _classify_expressions(
        self,
    ) -> Tuple[List[Column], List[Constraint]]:
        """TODO"""

        columns = []
        table_constraints = []

        for expression_ in self.expressions:
            first_tkn = expression_[0]
            first_tkn_name = str(first_tkn)
            other_tkns = expression_[1:]

            if first_tkn.match(Name, None):
                columns.append(Column(self, first_tkn_name, other_tkns))

            if first_tkn.match(Keyword, None):

                match first_tkn:
                    case "FOREIGN KEY":
                        table_constraints.append(TableForeignKey(self, other_tkns))

                    case "PRIMARY KEY":
                        table_constraints.append(TablePrimaryKey(self, other_tkns))

                    case "UNIQUE":
                        table_constraints.append(TableUnique(self, other_tkns))

                    case _:
                        print(f"Skipping unknown constraint <{first_tkn}>")

        return columns, table_constraints
