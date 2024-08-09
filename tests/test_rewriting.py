import os
import pytest
import logging
import sql2shacl
from rdflib import Graph
from rdflib.compare import isomorphic
from rdflib.namespace import SH

logger = logging.getLogger(__name__)

TESTCASES = [
    testcase_
    for testcase_ in os.listdir("testcases/")
    if os.path.isdir(os.path.join("testcases/", testcase_))
]


def write_test_output(file_path: str, serialized_graph: str):

    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)

    with open(file_path, "w") as file:
        file.write(serialized_graph)


def shape_up_and_compare(sql_path: str, actual_shapes_graph_path: str, mode: str):
    if mode == "w3c":
        out_file_name = "sql2shacl_shape_w3c.ttl"
    else:
        out_file_name = "sql2shacl_shape_thapa.ttl"

    generated_shapes_graph_path = os.path.join(os.path.dirname(sql_path), out_file_name)

    with open(sql_path, "r") as file:
        sql = file.read()

    serialized_shapes_graph = sql2shacl.rewrite(
        sql,
        base_iri="http://example.com/base/",
        log_level=logging.DEBUG,
        mode=mode,
    )

    logger.debug(serialized_shapes_graph)

    write_test_output(generated_shapes_graph_path, serialized_shapes_graph)

    shapes_graph = Graph().parse(data=serialized_shapes_graph, format="ttl")
    actual_shapes_graph = Graph().parse(source=actual_shapes_graph_path, format="ttl")

    if mode == "w3c":
        for s, p, o in actual_shapes_graph:
            if p == SH.minLength or p == SH.maxLength or p == SH.select:
                actual_shapes_graph.remove((s, p, o))

        for s, p, o in shapes_graph:
            if p == SH.select:
                shapes_graph.remove((s, p, o))

    assert isomorphic(shapes_graph, actual_shapes_graph) is True


@pytest.mark.parametrize("testcase_", TESTCASES)
def test_sql2shacl_sequeda(testcase_):
    create_sql = os.path.join("testcases", testcase_, "create.sql")
    actual_shapes_graph = os.path.join("testcases", testcase_, "shape_thapa.ttl")

    shape_up_and_compare(create_sql, actual_shapes_graph, mode="thapa")


@pytest.mark.parametrize("testcase_", TESTCASES)
def test_sql2shacl_w3c(testcase_):
    create_sql = os.path.join("testcases", testcase_, "create.sql")
    actual_shapes_graph = os.path.join("testcases", testcase_, "shape_w3c.ttl")

    shape_up_and_compare(create_sql, actual_shapes_graph, mode="w3c")
