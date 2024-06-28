import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from rdflib import URIRef
from ..utils.exceptions import UnsupportedSQLDatatypeException

with open(Path("sql2shacl") / "components" / "sqldatatype2xmlschema.json") as f:
    SQLDTYPE_XMLSCHEMA_MAP = json.loads(f.read())


class Builder(ABC):

    def __init__(self, base: str):
        self.base = base

    @abstractmethod
    def build_class_iri(self, rel_name: str) -> URIRef:
        pass

    @abstractmethod
    def build_attribute_iri(self, rel_name: str, attribute_name: str) -> URIRef:
        pass

    @abstractmethod
    def build_datatype_iri(self, dtype: str) -> URIRef:
        pass

    @abstractmethod
    def build_foreign_key_iri(
        self,
        rel_name: str,
        referenced_name: str,
        attributes: List[str],
        references: List[str],
    ) -> URIRef:
        pass

    @abstractmethod
    def build_foreign_key_iri_binary(
        self,
        bin_rel_name: str,
        referenced_name: str,
        other_referenced_name: str,
        referenced_attributes: List[str],
        other_referenced_attributes: List[str],
    ) -> URIRef:
        pass


class SequedaBuilder(Builder):

    def build_class_iri(self, rel_name: str) -> URIRef:
        return URIRef(self.base + rel_name)

    def build_attribute_iri(self, rel_name: str, attribute_name: str) -> URIRef:
        return URIRef(self.base + rel_name + "#" + attribute_name)

    def build_datatype_iri(self, dtype: str) -> URIRef:
        try:
            mapped = SQLDTYPE_XMLSCHEMA_MAP[dtype.upper()]
        except KeyError:
            raise UnsupportedSQLDatatypeException(
                f"SQL datatype <{dtype}> is not supported as of today."
            )
        return URIRef(mapped)

    def build_foreign_key_iri(
        self,
        rel_name: str,
        referenced_name: str,
        attributes: List[str],
        references: List[str],
    ) -> URIRef:
        rel_part = rel_name + "," + referenced_name
        attributes_part = ",".join(attributes) + "," + ",".join(references)
        return URIRef(self.base + rel_part + "#" + attributes_part)

    def build_foreign_key_iri_binary(
        self,
        bin_rel_name: str,
        referenced_name: str,
        other_referenced_name: str,
        referenced_attributes: List[str],
        other_referenced_attributes: List[str],
    ) -> URIRef:
        referenced_name_part = referenced_name + "," + other_referenced_name
        referenced_attributes_part = (
            ",".join(referenced_attributes)
            + ","
            + ",".join(other_referenced_attributes)
        )
        return URIRef(
            self.base
            + bin_rel_name
            + "#"
            + referenced_name_part
            + ","
            + referenced_attributes_part
        )


class DMBuilder(Builder):
    pass
