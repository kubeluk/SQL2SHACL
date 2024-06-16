import sqlparse
from sqlparse.sql import Identifier, Parenthesis
from sqlparse.tokens import Name, Keyword

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
        if stmt.get_type() == "CREATE":
            for tkn in stmt.tokens:
                if isinstance(tkn, Identifier):
                    print(f"rel: {tkn.get_real_name()}")
                if isinstance(tkn, Parenthesis):
                    for sub in tkn.flatten():
                        if not sub.is_whitespace:
                            # print(sub.ttype, sub)
                            if sub.match(Name, None):
                                print(f"col: {sub}")
                            if sub.match(Name.Builtin, None):
                                print(f"datatype: {sub}")
                            if sub.match(Keyword, None):
                                print(f"constraint: {sub}")


if __name__ == "__main__":
    main()
