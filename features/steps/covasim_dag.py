from pydoc import locate

import sys
sys.path.append("../") # This one's for running `behave` in `compare-inverventions`

from causcumber_utils import draw_connected_repeating_unit, iterate_repeating_unit, draw_connected_dag

import pygraphviz

use_step_matcher("parse")

# We need a special step definition to do the repeating unit for covasim since it
# records time steps daily but we want to aggregate them into weeks to reduce
# the size of the causal DAG. To do this, we simply divide the number of days by 7

@given("a covasim simulation with parameters")
def step_impl(context):
    """
    Populate the params_dict with the specified simulation parameters.

    :param context: The context
    :type context: behave.Context
    """
    for row in context.table:
        cast_type = locate(row["type"])
        context.params_dict[row["parameter"]] = cast_type(row["value"])
        context.types[row["parameter"]] = cast_type
    context.n_weeks = round(context.params_dict['n_days']/7)
