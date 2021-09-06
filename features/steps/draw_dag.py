from pydoc import locate

import sys
sys.path.append("../") # This one's for running `behave` in `compare-inverventions`

from causcumber_utils import draw_connected_repeating_unit, iterate_repeating_unit, draw_connected_dag

import pygraphviz

use_step_matcher("parse")

@given("the following variables are recorded {frequency}")
def step_impl(context, frequency):
    """
    Populate the datatypes and default values of the variables of interested
    as specified in the Background.
    
    :param context: The context
    :type context: behave.Context
    :param frequency: The frequency with which time steps are reported,
    e.g. "weekly", or "each time step".
    :type frequency: str
    """
    print("Frequency:", frequency)
    context.desired_outputs = []
    for row in context.table:
        context.types[row['variable']] = locate(row['type'])
        context.desired_outputs.append(row['variable'])
    context.frequency = frequency


@given(u'a connected repeating unit')
def step_impl(context):
    """
    Draw a connected repeating unit.
    
    :param context: The context
    :type context: behave.Context
    """
    inputs = list(context.params_dict.keys())
    context.repeating_unit = draw_connected_repeating_unit(inputs, context.desired_outputs)


@when(u'we prune the following edges')
def step_impl(context):
    """
    Prune the given edges from the connected repeating unit.
    
    :param context: The context
    :type context: behave.Context
    """
    for row in context.table:
        print(f"deleting edge {row['s1']} -> {row['s2']}")
        print(context.repeating_unit)
        context.repeating_unit.delete_edge(row['s1'], row['s2'])


@when(u'we add the following edges')
def step_impl(context):
    """
    Add the given edges to the repeating unit.
    
    :param context: The context
    :type context: behave.Context
    """
    for row in context.table:
        context.repeating_unit.add_edge(row['s1'], row['s2'])


@then(u'we obtain the causal DAG for {n} {time_steps}')
def step_impl(context, n, time_steps):
    """
    Iterate the repeating unit for the given number of time steps.
    
    :param context: The context
    :type context: behave.Context
    :param n: The number of time steps to iterate the repeating unit for
    :type n: int
    :param time_steps: The kind of time step we're interested in,
    e.g. "weeks", "days", or "time steps"
    :type time_steps: str
    """
    dag = iterate_repeating_unit(context.repeating_unit, int(n), start=1)
    dag.write(context.dag_path)
