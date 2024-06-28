import logging
import sql2shacl
from rdflib import Graph
from rdflib.compare import isomorphic


def test_1():
    with open("tests/ddl/ddl-1.sql") as file:
        test_ddl = file.read()

    shapes_graph = Graph().parse(
        data=sql2shacl.rewrite(
            test_ddl, out_path="tests/tmp/shapes_graph.ttl", log_level=logging.INFO
        ),
        format="ttl",
    )
    actual_shapes_graph = Graph().parse("tests/shacl/shape-1.ttl")

    assert isomorphic(shapes_graph, actual_shapes_graph) is True
