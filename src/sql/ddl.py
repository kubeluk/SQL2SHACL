import logging
import sqlparse
from typing import List, Dict, Tuple
from sqlparse.sql import Identifier, Parenthesis, Token, TokenList, Statement
from sqlparse.tokens import Name, Punctuation, Keyword
from .relation import Relation
from .identifier import is_valid_identifier

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
        surrounding_4_tkns = expression[punct_idx - 2 : punct_idx + 3]

        if len(surrounding_4_tkns) < 4:
            return True

        # check if punctionation is surrounded by parentheses and column names (= marks key constraint)
        elif (
            surrounding_4_tkns[0].match(Punctuation, "(")
            and surrounding_4_tkns[1].match(Name, None)
            and surrounding_4_tkns[2].match(Name, None)
            and surrounding_4_tkns[3].match(Punctuation, ")")
        ):
            return False

        else:
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

            if relation_name is None:
                logger.warning(
                    f"Skipping the following statement since it does not contain a relation name: <{str(stmt)}>"
                )

            elif not is_valid_identifier(relation_name):
                logger.warning(
                    f"Skipping the following statement since <{relation_name}> is not a valid SQL identifier: <{str(stmt)}>"
                )

            else:
                relation_details[relation_name] = expressions

        return relation_details

    def _break_down_relations(self) -> List[Relation]:
        """TODO"""

        return [
            Relation(rel_name, expressions)
            for rel_name, expressions in self.relation_details.items()
        ]

    def _is_other_relation_referencing(self, rel: Relation) -> bool:
        """TODO"""

        others = [other for other in self.relations if other.name != rel.name]

        for other_ in others:
            if rel.name in other_.referenced_relation_names:
                return True

        return False

    def is_relation_binary(self, rel: Relation) -> bool:
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

        if (
            not rel.references_itself  # 1 (in combination with 2)
            and rel.has_exactly_two_attributes  # 2
            and rel.do_all_columns_form_primary_key  # 2
            and rel.do_all_columns_reference  # 3, 4 (in combination with 2)
            and not rel.has_column_involved_in_two_distinct_foreign_keys()  # 5, 6
            and not rel.do_all_columns_form_foreign_key  # 7
            and not self._is_other_relation_referencing(rel)  # 8
        ):
            return True

        return False
