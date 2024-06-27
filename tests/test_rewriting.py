from rdflib import Graph
from rdflib.compare import isomorphic, similar
from constraint_rewriter import ConstraintRewriter


UNIQUE_COMPONENT_GRAPH = Graph().parse(
    "src/components/unique_values_constraint.ttl", format="ttl"
)


def test_1():
    with open("tests/ddl/ddl-1.sql") as file:
        test_ddl = file.read()

    cr = ConstraintRewriter.setup(test_ddl)
    cr.rewrite()

    generated_shapes_graph = cr.shapes_graph
    actual_shapes_graph = Graph().parse("tests/shacl/shape-1.ttl")
    actual_shapes_graph += UNIQUE_COMPONENT_GRAPH

    assert similar(generated_shapes_graph, actual_shapes_graph) is True
