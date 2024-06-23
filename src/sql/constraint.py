from typing import List, Tuple
from sqlparse.sql import Token
from sqlparse.tokens import Name, Keyword


class Constraint:

    def __init__(self, parent, name: str, expression: List[Token]):
        self.parent = parent
        self.name = name
        self.expression = expression

    def get_constraint_name(self) -> str:
        """TODO"""

        return self.name

    def get_relation_name(self) -> str:
        """TODO"""

        return self.parent.get_name()


class TableUnique(Constraint):

    def __init__(self, parent, expression: List[Token], name: str = "UNIQUE"):
        super().__init__(parent, name, expression)
        self.col_names = self._break_down_expression()

    def _break_down_expression(self) -> List[str]:
        """TODO"""

        col_names = []
        for tkn in self.expression:
            if tkn.match(Name, None):
                col_names.append(str(tkn))

        return col_names

    def get_col_names(self) -> List[str]:
        """TODO"""

        return self.col_names


class TablePrimaryKey(TableUnique):

    def __init__(self, parent, expression: List[Token]):
        super().__init__(parent, expression, name="PRIMARY KEY")


class TableForeignKey(Constraint):

    def __init__(self, parent, expression: List[Token]):
        super().__init__(parent, "FOREIGN KEY", expression)
        (
            self.unique,
            self.not_null,
            self.col_names,
            self.referenced_rel_name,
            self.referenced_col_names,
        ) = self._break_down_expression()

    def _break_down_expression(self) -> Tuple[bool, bool, List[str], str, List[str]]:
        """TODO"""

        unique = False
        not_null = False
        col_names = []
        referenced_rel_name = None
        referenced_col_names = []

        for idx, tkn in enumerate(self.expression):
            if tkn.match(Keyword, "UNIQUE"):
                unique = True

            if tkn.match(Keyword, "NOT NULL"):
                not_null = True

            if tkn.match(Name, None):
                col_names.append(str(tkn))

            if tkn.match(Keyword, "REFERENCES"):
                referenced_rel_name = self.expression[idx + 1]

                for ref in self.expression[idx + 2 :]:
                    if ref.match(Name, None):
                        referenced_col_names.append(ref)

        return not_null, unique, col_names, referenced_rel_name, referenced_col_names

    def get_column_names(self) -> List[str]:
        """TODO"""

        return self.col_names

    def get_referenced_relation_name(self) -> str:
        """TODO"""

        return self.referenced_rel_name

    def get_referenced_col_names(self) -> List[str]:
        """TODO"""

        return self.referenced_col_names

    def is_unique(self) -> bool:
        """TODO"""

        return self.unique

    def is_not_null(self) -> bool:
        """TODO"""

        return self.not_null


class ColumnForeignKey(Constraint):

    def __init__(self, parent, expression: List[Token]):
        super().__init__(parent, "REFERENCES", expression)
        self.col_name = parent.name
        self.referenced_rel_name, self.referenced_col_name = (
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
        referenced_rel_name = str(self.expression[0])

        if len(self.expression) == 1:
            referenced_col_name = self.col_name

        else:
            parenthesis_content = self.expression[1:]

            for tkn in parenthesis_content:
                if tkn.match(Name, None):
                    referenced_col_name = str(tkn)
                    break

        return referenced_rel_name, referenced_col_name

    def get_col_name(self) -> str:
        return self.col_name

    def get_referenced_rel_name(self) -> str:
        return self.referenced_rel_name

    def get_referenced_col_name(self) -> str:
        return self.referenced_col_name
