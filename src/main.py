import sqlparse
from sqlparse.sql import Identifier, Parenthesis, Token
from sqlparse.tokens import Name, Punctuation
from typing import List, Dict
from pprint import pprint


def _is_punctuation_part_of_constraint(punct: Token, tkn_list: List[Token]) -> bool:
    """Returns if punctionation is part of a constraint.

    This happens when specifying key constraints like:
        PRIMARY KEY (x_id, y_id)
    """

    punct_idx = tkn_list.index(punct)
    tkn_before = tkn_list[punct_idx - 1]
    tkn_after = tkn_list[punct_idx + 1]

    # check if punctionation is surrounded by column names
    if tkn_before.match(Name, None) and tkn_after.match(Name, None):
        return True

    return False


def parse_ddl(ddl: str) -> Dict[str, List[List[Token]]]:
    """TODO:"""

    parsed = sqlparse.parse(ddl)
    relation_details = {}

    for stmt in parsed:
        relation_name = None
        expressions = []

        for tkn in stmt.tokens:
            if isinstance(tkn, Identifier):
                relation_name = tkn.get_real_name()

            if isinstance(tkn, Parenthesis):
                parenthesis_content = list(tkn.flatten())[1:-1]
                non_whitespace_subtkns = [
                    sub for sub in parenthesis_content if not sub.is_whitespace
                ]
                expression_ = []

                for idx, sub in enumerate(non_whitespace_subtkns):
                    if idx == (len(non_whitespace_subtkns) - 1):
                        # last subtkn in list
                        expression_.append(sub)
                        expressions.append(expression_)
                        expression_ = []

                    if sub.match(Punctuation, ","):
                        if not _is_punctuation_part_of_constraint(
                            sub, non_whitespace_subtkns
                        ):
                            # punctionation marks end of expression
                            expressions.append(expression_)
                            expression_ = []
                            continue

                    expression_.append(sub)

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
