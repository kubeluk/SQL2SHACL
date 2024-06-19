import json
from pathlib import Path
from typing import List
from rdflib import URIRef
from utils.exceptions import UnsupportedSQLDatatypeException

BASE = "http://to.do/"

with open(Path("src/components") / "sqldatatype2xmlschema.json") as f:
    SQLDTYPE_XMLSCHEMA_MAP = json.loads(f.read())


def build_class_iri(rel_name: str) -> URIRef:
    return URIRef(BASE + rel_name)


def build_attribute_iri(rel_name: str, attribute_name: str) -> URIRef:
    return URIRef(BASE + rel_name + "#" + attribute_name)


def build_datatype_iri(dtype: str) -> URIRef:
    try:
        mapped = SQLDTYPE_XMLSCHEMA_MAP[dtype]
    except KeyError:
        raise UnsupportedSQLDatatypeException(
            f"SQL datatype <{dtype}> is not supported as of today."
        )
    return URIRef(mapped)


def build_foreign_key_iri(
    rel_name: str, referenced_name: str, attributes: List[str], references: List[str]
) -> URIRef:
    rel_part = rel_name + "," + referenced_name
    attributes_part = ",".join(attributes) + "," + ",".join(references)
    return URIRef(BASE + rel_part + "#" + attributes_part)


def build_foreign_key_iri_binary(
    bin_rel_name: str,
    referenced_name: str,
    other_referenced_name: str,
    referenced_attributes: List[str],
    other_referenced_attributes: List[str],
) -> URIRef:
    referenced_name_part = referenced_name + "," + other_referenced_name
    referenced_attributes_part = (
        ",".join(referenced_attributes) + "," + ",".join(other_referenced_attributes)
    )
    return URIRef(
        BASE
        + bin_rel_name
        + "#"
        + referenced_name_part
        + ","
        + referenced_attributes_part
    )
