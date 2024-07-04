import os
import pytest
import logging
import sql2shacl
from rdflib import Graph
from rdflib.compare import isomorphic

logger = logging.getLogger(__name__)

TESTCASES = [
    testcase_
    for testcase_ in os.listdir("testcases/")
    if os.path.isdir(os.path.join("testcases/", testcase_))
]


def shape_up_and_compare(sql_path: str, actual_shapes_graph_path: str):
    generated_shapes_graph_path = os.path.join(
        os.path.dirname(sql_path), "sql2shacl_shape.ttl"
    )

    with open(sql_path, "r") as file:
        sql = file.read()

    shapes_graph = Graph().parse(
        data=sql2shacl.rewrite(
            sql,
            base_iri="http://example.com/base/",
            out_path=generated_shapes_graph_path,
            log_level=logging.DEBUG,
        ),
        format="ttl",
    )

    actual_shapes_graph = Graph().parse(actual_shapes_graph_path)

    assert isomorphic(shapes_graph, actual_shapes_graph) is True


@pytest.mark.parametrize("testcase_", TESTCASES)
def test_sql2shacl(testcase_):
    create_sql = os.path.join("testcases", testcase_, "create.sql")
    actual_shapes_graph = os.path.join("testcases", testcase_, "shape_v2.ttl")

    shape_up_and_compare(create_sql, actual_shapes_graph)
