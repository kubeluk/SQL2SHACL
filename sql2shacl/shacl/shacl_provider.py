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

    _b_nodes = {}

    def __init__(self, rel: URIRef, path_obj: URIRef, class_obj: URIRef, b_node: BNode):
        super().__init__()
        self._b = b_node
        self.g.add((rel, SH.property, b_node))
        self.g.add((b_node, SH.path, path_obj))
        self.g.add((b_node, SH.nodeKind, SH.IRI))
        self.g.add((b_node, SH["class"], class_obj))

    @property
    def blank_node(self) -> BNode:
        return self._b

    @classmethod
    def shape(cls, rel: URIRef, path_obj: URIRef, class_obj: URIRef):
        _b = cls._b_nodes.get((rel, path_obj, class_obj), None)

        if _b is None:
            _b = BNode()
            cls._b_nodes[(rel, path_obj, class_obj)] = _b

        return Prop(rel, path_obj, class_obj, _b)


class MaxProp(Prop):

    @classmethod
    def shape(cls, rel: URIRef, path_obj: URIRef, class_obj: URIRef):
        prop = Prop.shape(rel, path_obj, class_obj)
        print(prop.g.serialize())
        prop.g.add((prop.blank_node, SH.maxCount, Literal(1)))
        print(prop.g.serialize())
        return prop


class CrdProp(MaxProp):

    @classmethod
    def shape(cls, rel: URIRef, path_obj: URIRef, class_obj: URIRef):
        maxprop = MaxProp.shape(rel, path_obj, class_obj)
        maxprop.g.add((maxprop.blank_node, SH.minCount, Literal(1)))
        return maxprop


class InvProp(Prop):

    @classmethod
    def shape(cls, rel: URIRef, inv_path_obj: URIRef, class_obj: URIRef):
        _b = BNode()
        prop = Prop.shape(rel, _b, class_obj)
        prop.g.add((_b, SH.inversePath, inv_path_obj))
        return prop


class InvMaxProp(InvProp):

    @classmethod
    def shape(cls, rel: URIRef, inv_path_obj: URIRef, class_obj: URIRef):
        invprop = InvProp.shape(rel, inv_path_obj, class_obj)
        invprop.g.add((invprop.blank_node, SH.maxCount, Literal(1)))
        return invprop


class Data(Shape):

    _b_nodes = {}

    def __init__(self, rel: URIRef, path_obj: URIRef, dtype: URIRef, b_node: BNode):
        super().__init__()
        self._b = b_node
        self.g.add((rel, SH.property, b_node))
        self.g.add((b_node, SH.path, path_obj))
        self.g.add((b_node, SH.nodeKind, SH.Literal))
        self.g.add((b_node, SH.datatype, dtype))

    @property
    def blank_node(self) -> BNode:
        return self._b

    @classmethod
    def shape(cls, rel: URIRef, path_obj: URIRef, dtype: URIRef):
        _b = cls._b_nodes.get((rel, path_obj, dtype), None)

        if _b is None:
            _b = BNode()
            cls._b_nodes[(rel, path_obj, dtype)] = _b

        return Data(rel, path_obj, dtype, _b)


class MaxData(Data):

    @classmethod
    def shape(cls, rel: URIRef, path_obj: URIRef, dtype: URIRef):
        data = Data.shape(rel, path_obj, dtype)
        data.g.add((data.blank_node, SH.maxCount, Literal(1)))
        return data


class CrdData(MaxData):

    @classmethod
    def shape(cls, rel: URIRef, path_obj: URIRef, dtype: URIRef):
        maxdata = MaxData.shape(rel, path_obj, dtype)
        maxdata.g.add((maxdata.blank_node, SH.minCount, Literal(1)))
        return maxdata


class UnqTuple(Shape):

    def __init__(self, rel: URIRef, *unq_props: URIRef):
        super().__init__()
        _b = BNode()
        self.g.add((rel, UQ["uniqueValuesForClass"], _b))
        for unq_prop_ in unq_props:
            self.g.add((_b, UQ["unqProp"], unq_prop_))
        self.g.add((_b, UQ["unqForClass"], rel))

    @classmethod
    def shape(cls, rel: URIRef, *unq_props: URIRef):
        return UnqTuple(rel, *unq_props)


class Node(Shape):

    def __init__(self, rel: URIRef):
        super().__init__()
        self.g.add((rel, RDF.type, SH.NodeShape))
        self.g.add((rel, RDF.type, RDFS.Class))

    @classmethod
    def shape(cls, rel: URIRef):
        return Node(rel)
