from typing import List
from rdflib import URIRef
from sqlparse.sql import Token
from sqlparse.tokens import Name, Punctuation, Keyword
from table_parser import parse_ddl
from shacl_provider import Shape, MaxData, CrdData
from table_classifier import is_relation_binary
from iri_builder import (
    build_class_iri,
    build_attribute_iri,
    build_datatype_iri,
    build_foreign_key_iri,
    build_foreign_key_iri_binary,
)


def _handle_table_constraint(shape: Shape, expression: List[Token]) -> None:
    """Handles expressions that start with a Token of ttype Keyword.

    This is the case for expressions that only define constraints, e.g.:
        PRIMARY KEY (ToEmp, ToPrj)
    """

    constraint = expression[0]

    match constraint:
        case "PRIMARY KEY":
            pass
        case "FOREIGN KEY":
            pass
        case "UNIQUE":
            pass
        case _:
            # TODO: log unhandled constraint
            return


def _handle_datatype(
    col_name: str, dtype: str, shape: Shape, expression: List[Token]
) -> None:
    """TODO"""

    attribute_uri = build_attribute_iri(col_name)
    mapped_xmlschema_type_uri = build_datatype_iri(dtype)

    for tkn in expression:
        if str(tkn) == "NOT NULL":
            return shape.add(CrdData(attribute_uri, mapped_xmlschema_type_uri))

    return shape.add(MaxData(attribute_uri, mapped_xmlschema_type_uri))


def _handle_unique(shape: Shape, expression: List[Token]) -> None:
    for tkn in expression:
        if str(tkn) == "UNIQUE":
            pass


def _handle_primary_key(shape: Shape, expression: List[Token]) -> None:
    for tkn in expression:
        if str(tkn) == "PRIMARY KEY":
            pass


def _handle_references(shape: Shape, expression: List[Token]) -> None:
    for tkn in expression:
        if str(tkn) == "REFERENCES":
            pass


def _handle_column_constraint(shape: Shape, expression: List[Token]) -> None:
    """TODO"""

    col_name = expression[0]
    dtype = expression[1]
    constraints = expression[2:]

    _handle_datatype(col_name, dtype, shape, constraints)

    _handle_unique()

    _handle_primary_key()

    _handle_references()

    for tkn in expression[2:]:
        if str(tkn) == "PRIMARY KEY":
            pass

        if str(tkn) == "REFERENCES":
            pass

        if str(tkn) == "UNIQUE":
            pass

        print(tkn, tkn.ttype)

    print("\n")


def build_shapes(relation_details: dict) -> None:
    """Gets the output of table_parser.parse_ddl() and builds SHACL shapes from it.

    Token.Name: column name
    Token.Name.Builtin: data type
    Token.Keyword: constraint
    Token.Punctuation: parenthesis
    """

    shapes = {}

    for rel_name, expressions in relation_details.items():
        if not is_relation_binary(expressions):  # TODO: impelement is_relation_binary()
            shape = Shape(build_class_iri(rel_name))
            shapes[rel_name] = shape

            # TODO: add logging which expressions haven't been handled
            for expression_ in expressions:
                first_tkn = expression_[0]

                if first_tkn.match(Name, None):
                    _handle_column_constraint(shape, expression_)

                if first_tkn.match(Keyword, None):
                    _handle_table_constraint(shape, expression_)

        else:
            pass  # TODO: handle binary relations


if __name__ == "__main__":
    DDL = """
        CREATE TABLE Emp (
            E_id integer PRIMARY KEY,
            Name text CONSTRAINT test_constraint NOT NULL,
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
    build_shapes(relation_details)
