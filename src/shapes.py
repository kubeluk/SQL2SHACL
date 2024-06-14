from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, SH


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


# TODO: implement UnqTuple


class Shape:

    g = Graph()

    def __init__(self, node: URIRef):
        self.node = node
        self.g.add((node, RDF.type, SH.NodeShape))
        self.g.add((node, RDF.type, RDFS.Class))

    def add_property(self, p: Base) -> None:
        self.g.add((self.node, SH.property, p._b))
        self.g += p.g


if __name__ == "__main__":
    shape = Shape(URIRef("http://example.org/shapes#1"))
    prop = InvMaxProp(
        URIRef("http://example.org/props#1"), URIRef("http://example.org/props#2")
    )
    shape.add_property(prop)
    print(shape.g.serialize())
