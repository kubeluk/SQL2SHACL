"""
Copyright 2024 Lukas Kubelka and Xuemin Duan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

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
        referenced_attribute: List[str],
        other_referenced_attribute: List[str],
    ) -> URIRef:
        referenced_name_part = referenced_name + "," + other_referenced_name
        referenced_attributes_part = (
            referenced_attribute + "," + other_referenced_attribute
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
