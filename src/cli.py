# TODO: build command-line functionality
import logging
from constraint_rewriter import ConstraintRewriter
from utils.exceptions import MissingSQLDatatypeException
from utils.logging import setup_logging


def main():
    ddl_script = """
        CREATE TABLE Emp (
            E_id integer PRIMARY KEY,
            Name char CONSTRAINT test_constraint NOT NULL,
            Post char
        );
        CREATE TABLE Acc (
            A_id integer,
            Name char UNIQUE,
            PRIMARY KEY (A_id)
        );
        CREATE TABLE Prj (
            P_id integer PRIMARY KEY,
            Name char NOT NULL,
            ToAcc integer NOT NULL UNIQUE REFERENCES Acc (A_id)
        );
        CREATE TABLE Asg (
            ToEmp integer REFERENCES Emp (E_id),
            ToPrj integer REFERENCES Prj (P_id),
            PRIMARY KEY (ToEmp, ToPrj)
        );
    """

    setup_logging(log_level=logging.INFO)

    cr = ConstraintRewriter.setup(ddl_script)

    try:
        cr.rewrite()
    except MissingSQLDatatypeException:
        pass

    # cr.print_parsed_ddl()
    # print("\n" + (80 * "#") + "\n")
    # cr.print_shapes()


if __name__ == "__main__":
    main()
