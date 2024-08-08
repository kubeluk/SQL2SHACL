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

import logging
import json
import urllib.parse

from functools import wraps
from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import List
from rdflib import URIRef
from ..utils.exceptions import UnsupportedSQLDatatypeException

with open(Path("sql2shacl") / "components" / "sqldatatype2xmlschema.json") as f:
    SQLDTYPE_XMLSCHEMA_MAP = json.loads(f.read())

logger = logging.getLogger(__name__)


class IRISafe:

    def iri_safe(string):
        # Define the characters that should be considered safe.
        # These include unreserved characters as well as non-ASCII characters (e.g., Chinese).
        def is_iunreserved(char):
            # Define the unreserved characters according to RFC 3987
            return (
                "A" <= char <= "Z"
                or "a" <= char <= "z"
                or "0" <= char <= "9"
                or char in "-._~"
                or ord(char) > 0x7F  # Allow non-ASCII characters
            )

        # Percent-encode only those characters not in the iunreserved set
        return "".join(
            char if is_iunreserved(char) else urllib.parse.quote(char, safe="")
            for char in string
        )

    def recursive_iri_safe(value):
        """%-escape strings used for URIs recursively."""

        if isinstance(value, str):
            return IRISafe.iri_safe(value)
        elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            return type(value)(IRISafe.recursive_iri_safe(item) for item in value)
        else:
            return value

    def iri_safe_params(func):
        """Decorator that %-escapes strings used for URIs."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            quoted_args = [IRISafe.recursive_iri_safe(arg) for arg in args]
            quoted_kwargs = {
                k: IRISafe.recursive_iri_safe(v) for k, v in kwargs.items()
            }

            return func(*quoted_args, **quoted_kwargs)

        return wrapper


class Builder(ABC):

    def __init__(self, base: str):
        self.base = urllib.parse.quote(base, ":/")

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
        col_name: str,
        other_col_name: str,
        referenced_col_name: str,
        other_referenced_col_name: str,
    ) -> URIRef:
        pass


class SequedaBuilder(Builder):

    @IRISafe.iri_safe_params
    def build_class_iri(self, rel_name: str) -> URIRef:
        return URIRef(self.base + rel_name)

    @IRISafe.iri_safe_params
    def build_attribute_iri(self, rel_name: str, attribute_name: str) -> URIRef:
        return URIRef(self.base + rel_name + "#" + attribute_name)

    @IRISafe.iri_safe_params
    def build_datatype_iri(self, dtype: str) -> URIRef:
        try:
            mapped = SQLDTYPE_XMLSCHEMA_MAP[dtype.upper()]
        except KeyError:
            raise UnsupportedSQLDatatypeException(
                f"SQL datatype <{dtype}> is not supported as of today."
            )
        return URIRef(mapped)

    @IRISafe.iri_safe_params
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

    @IRISafe.iri_safe_params
    def build_foreign_key_iri_binary(
        self,
        bin_rel_name: str,
        col_name: str,
        other_col_name: str,
        referenced_col_name: str,
        other_referenced_col_name: str,
    ) -> URIRef:
        col_names = col_name + "," + other_col_name
        referenced_col_names = referenced_col_name + "," + other_referenced_col_name
        return URIRef(
            self.base + bin_rel_name + "#" + col_names + "," + referenced_col_names
        )
