"""
Check a protocol for various properties, such as consistency
"""
import pysmt.shortcuts

from paml_check.activity_graph import ActivityGraph
from paml_check.utils import print_debug
from paml_check.schedule import Schedule

__all__ = ['check_doc']


def check_doc(doc):
    """
    Check a paml document for temporal consistency
    :param doc:
    :return:
    """
    graph = ActivityGraph(doc)
    # graph.print_debug()

    formula = graph.generate_constraints()
    result = check(formula)
    if result:
        s = Schedule(result, graph)
        return s, graph
    else:
        return None, graph

def get_minimum_duration(doc):
    """
    Get minimum duration for each protocol in doc
    :param doc:
    :return: minimum duration dict, indexed by protocol id
    """
    graph = ActivityGraph(doc)
    duration = graph.get_minimum_duration()
    return duration

def check(formula):
    """
    Check whether a formula is satisfiable and return the model if so
    :param formula:
    :return:
    """
    return pysmt.shortcuts.get_model(formula)
