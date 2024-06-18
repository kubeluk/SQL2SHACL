import sqlparse
from sqlparse.sql import Identifier, Parenthesis, Token, TokenList
from sqlparse.tokens import Name, Punctuation
from typing import List, Dict
from pprint import pprint


def _is_punctuation_end_of_expression(punct: Token, expression: List[Token]) -> bool:
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


def _is_last_tkn_in_list(tkn: Token, tkn_list: List[Token]) -> bool:
    """Returns True if the token is the last element in the list."""

    return tkn_list.index(tkn) == (len(tkn_list) - 1)


def _get_parenthesis_subtkns(parenthesis_tkn: TokenList) -> List[Token]:
    """Returns the list of tokens with the starting and ending parentheses and 'Whitespace' removed."""

    content = list(parenthesis_tkn.flatten())[1:-1]
    return [tkn for tkn in content if not tkn.is_whitespace]


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
                subtkns = _get_parenthesis_subtkns(tkn)
                expression_ = []

                for subtkn_ in subtkns:
                    if _is_last_tkn_in_list(subtkn_, subtkns):
                        expression_.append(subtkn_)
                        expressions.append(expression_)
                        expression_ = []

                    if subtkn_.match(Punctuation, ","):
                        if _is_punctuation_end_of_expression(subtkn_, subtkns):
                            expressions.append(expression_)
                            expression_ = []
                            continue

                    expression_.append(subtkn_)

        relation_details[relation_name] = expressions

    return relation_details


if __name__ == "__main__":
    DDL = """
        CREATE TABLE Emp (
            E_id integer PRIMARY KEY,
            Name text NOT NULL,
            Post text
        );
        CREATE TABLE Acc (
            A_id integer PRIMARY KEY,
            Name text UNIQUE
        );
        CREATE TABLE Prj (
            P_id integer PRIMARY KEY,
            Name text NOT NULL,
            ToAcc integer NOT NULL UNIQUE REFERENCES Acc (A_id)
        );
        CREATE TABLE Asg (
            ToEmp integer REFERENCES Emp (E_id),
            ToPrj integer REFERENCES Prj (P_id),
            PRIMARY KEY (ToEmp, ToPrj)
        );
    """

    relation_details = parse_ddl(DDL)
    pprint(relation_details)
