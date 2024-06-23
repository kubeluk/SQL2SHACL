import sqlparse
from typing import List, Dict
from sqlparse.sql import Identifier, Parenthesis, Token, TokenList
from sqlparse.tokens import Name, Punctuation
from .relation import Relation


class DDL:
    """TODO

    ---
    Token.Name:         column name
    Token.Name.Builtin: data type
    Token.Keyword:      constraint
    Token.Punctuation:  parenthesis
    """

    def __init__(self, ddl_script: str):
        self.parsed = sqlparse.parse(ddl_script)
        self.relation_details = self._break_down_statements()
        self.relations = self._break_down_relations()

    def get_relation_details(self) -> Dict[str, List[List[Token]]]:
        """TODO"""

        return self.relation_details

    def get_relation_names(self) -> List[str]:
        """TODO"""

        return [rel_name for rel_name in self.relation_details.keys()]

    def get_relations(self) -> List[Relation]:
        """TODO"""

        return self.relations

    def get_relation_expressions(self, rel_name: str) -> List[List[Token]]:
        """TODO"""

        return self.relation_details[rel_name]

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
    def _is_end_of_parentesis_content(tkn: Token, tkn_list: List[Token]) -> bool:
        """Returns True if the token is the last element in the list."""

        return tkn_list.index(tkn) == (len(tkn_list) - 1)

    @staticmethod
    def _get_parenthesis_content(parenthesis_tkn: TokenList) -> List[Token]:
        """Returns the list of tokens with the starting and ending parentheses and 'Whitespace' removed."""

        content = list(parenthesis_tkn.flatten())[1:-1]
        return [tkn for tkn in content if not tkn.is_whitespace]

    def _break_down_statements(self) -> Dict[str, List[List[Token]]]:
        """TODO"""

        relation_details = {}

        for stmt in self.parsed:
            relation_name = None
            expressions = []

            for tkn in stmt.tokens:
                if isinstance(tkn, Identifier):
                    relation_name = tkn.get_real_name()

                if isinstance(tkn, Parenthesis):
                    content = DDL._get_parenthesis_content(tkn)
                    expression_ = []

                    for subtkn in content:
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

            relation_details[relation_name] = expressions

        return relation_details

    def _break_down_relations(self) -> List[Relation]:
        """TODO"""

        return [
            Relation(rel_name, expressions)
            for rel_name, expressions in self.relation_details.items()
        ]

    def is_relation_binary(self, rel_name: str) -> bool:
        """Returns if a relation is a binary relation

        Informally, a relation R is a binary relation between two relations S and T if:

            1. both S and T are different from R
            2. R has exactly two attributes A and B, which form a primary key of R
            3. A is the attribute of a foreign key in R that points to S
            4. B is the attribute of a foreign key in R that points to T
            5. A is not the attribute of two distinct foreign keys in R
            6. B is not the attribute of two distinct foreign keys in R
            7. A and B are not the attributes of a composite foreign key in R
            8. relation R does not have incoming foreign keys

        See Sequeda2012 [1] for details.

        Example for a binary relation:
        ```
        CREATE TABLE Asg (
            ToEmp integer REFERENCES Emp (E_id),
            ToPrj integer REFERENCES Prj (P_id),
            PRIMARY KEY (ToEmp, ToPrj)
        )
        ```

        [1] https://doi.org/10.1145/2187836.2187924
        """

        return False
