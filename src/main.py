import sqlparse
from sqlparse.sql import Identifier, Parenthesis

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


def main():
    parsed = sqlparse.parse(DDL)
    for stmt in parsed:
        for tkn_ in stmt.tokens:
            if isinstance(tkn_, Identifier):
                print(tkn_)
            if isinstance(tkn_, Parenthesis):
                for sub in tkn_.tokens:
                    print(sub)
        break


if __name__ == "__main__":
    main()
