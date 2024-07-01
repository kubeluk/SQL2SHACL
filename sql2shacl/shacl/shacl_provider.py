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

from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import RDF, RDFS, SH

UQ = Namespace("http://sirius−labs.no/shapes/unique#")


class Shape:

    def __init__(self):
        self.g = Graph()

    def __iter__(self):
        return iter(self.g)

    def __iadd__(self, other):
        if isinstance(other, Graph):
            other += self.g
        else:
            raise TypeError("Cannot add Shape to non-Graph object")
        return self

    @property
    def graph(self) -> Graph:
        return self.g


class Prop(Shape):

    def __init__(self, rel: URIRef, path: URIRef, cls: URIRef):
        super().__init__()
        self._b = BNode()
        self.g.add((rel, SH.property, self._b))
        self.g.add((self._b, SH.path, path))
        self.g.add((self._b, SH.nodeKind, SH.IRI))
        self.g.add((self._b, SH["class"], cls))


class MaxProp(Prop):

    def __init__(self, rel: URIRef, path: URIRef, cls: URIRef):
        super().__init__(rel, path, cls)
        self.g.add((self._b, SH.maxCount, Literal(1)))


class CrdProp(MaxProp):

    def __init__(self, rel: URIRef, path: URIRef, cls: URIRef):
        super().__init__(rel, path, cls)
        self.g.add((self._b, SH.minCount, Literal(1)))


class InvProp(Prop):

    def __init__(self, rel: URIRef, inv_path: URIRef, cls: URIRef):
        _b = BNode()
        super().__init__(rel, _b, cls)
        self.g.add((_b, SH.inversePath, inv_path))


class InvMaxProp(InvProp):

    def __init__(self, rel: URIRef, inv_path: URIRef, cls: URIRef):
        super().__init__(rel, inv_path, cls)
        self.g.add((self._b, SH.maxCount, Literal(1)))


class Data(Shape):

    def __init__(self, rel: URIRef, path: URIRef, dtype: URIRef):
        super().__init__()
        self._b = BNode()
        self.g.add((rel, SH.property, self._b))
        self.g.add((self._b, SH.path, path))
        self.g.add((self._b, SH.nodeKind, SH.Literal))
        self.g.add((self._b, SH.datatype, dtype))


class MaxData(Data):

    def __init__(self, rel: URIRef, path: URIRef, dtype: URIRef):
        super().__init__(rel, path, dtype)
        self.g.add((self._b, SH.maxCount, Literal(1)))


class CrdData(MaxData):

    def __init__(self, rel: URIRef, path: URIRef, dtype: URIRef):
        super().__init__(rel, path, dtype)
        self.g.add((self._b, SH.minCount, Literal(1)))


class UnqTuple(Shape):

    def __init__(self, rel: URIRef, *unq_props: URIRef):
        super().__init__()
        _b = BNode()
        self.g.add((rel, UQ["uniqueValuesForClass"], _b))
        for unq_prop_ in unq_props:
            self.g.add((_b, UQ["unqProp"], unq_prop_))
        self.g.add((_b, UQ["unqForClass"], rel))


class Node(Shape):

    def __init__(self, rel: URIRef):
        super().__init__()
        self.g.add((rel, RDF.type, SH.NodeShape))
        self.g.add((rel, RDF.type, RDFS.Class))
