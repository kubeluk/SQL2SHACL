from typing import Union
from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import RDF, RDFS, SH

UQ = Namespace("http://sirius−labs.no/shapes/unique#")


class Base:

    g = Graph()
    _b = BNode()

    def __init__(self, path: URIRef):
        self.path = path
        self.g.add((self._b, SH.path, path))


class Prop(Base):

    def __init__(self, path: URIRef, cls: URIRef):
        super().__init__(path)
        self.g.add((self._b, SH.nodeKind, SH.IRI))
        self.g.add((self._b, SH["class"], cls))


class MaxProp(Prop):

    def __init__(self, path: URIRef, cls: URIRef):
        super().__init__(path, cls)
        self.g.add((self._b, SH.maxCount, Literal(1)))


class CrdProp(MaxProp):

    def __init__(self, path: URIRef, cls: URIRef):
        super().__init__(path, cls)
        self.g.add((self._b, SH.minCount, Literal(1)))


class InvProp(Prop):

    _b_inv = BNode()

    def __init__(self, inv_path: URIRef, cls: URIRef):
        super().__init__(self._b_inv, cls)
        self.g.add((self._b_inv, SH.inversePath, inv_path))


class InvMaxProp(InvProp):

    def __init__(self, inv_path: URIRef, cls: URIRef):
        super().__init__(inv_path, cls)
        self.g.add((self._b, SH.maxCount, Literal(1)))


class Data(Base):

    def __init__(self, path: URIRef, dtype: URIRef):
        super().__init__(path)
        self.g.add((self._b, SH.nodeKind, SH.Literal))
        self.g.add((self._b, SH.datatype, dtype))


class MaxData(Data):

    def __init__(self, path: URIRef, dtype: URIRef):
        super().__init__(path, dtype)
        self.g.add((self._b, SH.maxCount, Literal(1)))


class CrdData(MaxData):

    def __init__(self, path: URIRef, dtype: URIRef):
        super().__init__(path, dtype)
        self.g.add((self._b, SH.minCount, Literal(1)))


class UnqTuple:

    g = Graph()
    _b = BNode()

    def __init__(self, cls: URIRef, *unq_props: URIRef):
        for unq_prop_ in unq_props:
            self.g.add((self._b, UQ["unqProp"], unq_prop_))
        self.g.add((self._b, UQ["unqForClass"], cls))


class Shape:

    g = Graph()
    unq_component = Graph()

    def __init__(self, node: URIRef):
        self.node = node
        self.g.add((node, RDF.type, SH.NodeShape))
        self.g.add((node, RDF.type, RDFS.Class))

    def add(self, x: Union[Base, UnqTuple]) -> None:
        if isinstance(x, Base):
            self._add_property(x)
        elif isinstance(x, UnqTuple):
            self._add_unique(x)
        else:
            raise ValueError(
                f"Input should be of type Union[Base, UnqTuple]. You gave {type(x)}."
            )

    def _add_property(self, p: Base) -> None:
        self.g.add((self.node, SH.property, p._b))
        self.g += p.g

    def _add_unique(self, u: UnqTuple) -> None:
        if len(self.unq_component) == 0:
            self.unq_component = self.unq_component.parse(
                "src/components/unique_values_constraint.ttl", format="ttl"
            )
            self.g += self.unq_component

        self.g.add((self.node, UQ["uniqueValuesForClass"], u._b))
        self.g += u.g


if __name__ == "__main__":
    shape = Shape(URIRef("http://example.org/shapes#1"))
    x = UnqTuple(
        URIRef("http://example.org/props#1"), URIRef("http://example.org/props#2")
    )
    shape.add(x)
    print(shape.g.serialize())
