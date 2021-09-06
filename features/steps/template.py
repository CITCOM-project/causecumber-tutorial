import sys
sys.path.append("../") # This one's for running `behave` in `compare-inverventions`

from causcumber_utils import run_dowhy, test

from pydoc import locate

from behave import use_step_matcher

import pandas as pd

use_step_matcher("parse") # allows us to match steps with placeholder variables

def run_the_model(params):
    """
    Run the model given the parameters. You obviously need to implement this
    to suite the requirements of your own model. If you are only using
    pre-existing runtime data, you do not need to implement this method and
    should instead use the @observational('location/of/csv_file.csv') tag to
    specify the location of the observational data.

    :param params: The parameters with which to run your model.
    :type params: dict
    :return: Pandas DataFrame representing the run(s) of your model in which
    each row represents a single run and each column represents a variable as
    specified in the Background.
    :rtype: pandas.DataFrame
    """
    raise NotImplementedError('run_the_model(params)')


@given(u'a simulation with parameters')
def step_impl(context):
    """
    Populate the datatypes and parameters dictionaries from the Background table.

    :param context: The context
    :type context: behave.Context
    """
    for row in context.table:
        cast_type = locate(row["type"])
        context.params_dict[row["parameter"]] = cast_type(row["value"])
        context.types[row["parameter"]] = cast_type

# This will match any input with any value so we don't need a separate step def for each variable/value pair
@given(u'we run the model with {treatment_var}={control_value}')
def step_impl(context, treatment_var, control_value):
    """
    Run the model with the given input configuration, representing the control.

    :param context: The context
    :type context: behave.Context
    :param treatment_var: The name of the treatment variable
    :type treatment_var: string
    :param control_value: The control value of the variable
    :type control_value: string
    """
    context.treatment_var = treatment_var # declare the treatment variable for when we run doWhy
    context.control_val = control_value # declare the control value of the treatment variable for when we run dowhy

    if not context.observational: # This checks to see if we're using observational data
        # Copy the params dict and update the input of interest by casting to the correct type
        params = context.params_dict.copy()
        params[treatment_var] = context.types[treatment_var](control_value)

        # run the model
        context.data = run_the_model(params)


@when(u'we run the model with {treatment_var}={treatment_value}')
def step_impl(context, treatment_var, treatment_value):
    """
    Run the model with the given input configuration, representing the treatment.

    :param context: The context
    :type context: behave.Context
    :param treatment_var: The name of the treatment variable
    :type treatment_var: string
    :param treatment_value: The treatment value of the variable
    :type treatment_value: string

    """
    if treatment_var != context.treatment_var:
        raise ValueError("Treatment variables in Given and When steps should be the same")

    context.treatment_val = treatment_value # declare the treatment value of the treatment variable for when we run dowhy

    if not context.observational: # Check if we're using observational data

        params = context.params_dict.copy()
        params[input] = context.types[input](treatment_value)

        # run the model and add the resulting dataframe to the context data
        context.data = pd.concat([context.data, run_the_model(params)])


@then(u'the {outcome_var} should be {relationship} control')
def step_impl(context, relationship):
    """
    Perform the causal inference test to see if the difference between the
    control and treatment is as expected.

    :param context: The context
    :type context: behave.context
    :param relationship: The expected relationship between the control and
    treatment, for example ">", "<", or "=".
    :type relationship: string
    """
    estimate, (ci_low, ci_high) = run_dowhy(
        "path/to/csv_file.csv",
        "dags/template.dot", # This should be the name of the feature file in "snake case"
        context.treatment_var,
        outcome_var,
        context.control_val,
        context.treatment_val,
        method_name="backdoor.linear_regression") # use whatever estimation method is most appropriate
    # This supports >, <, and = but it should be easy to add your own
    test(estimate, relationship, ci_low, ci_high)


@then(u'the effect on {outcome_var} should be {effect}')
def step_impl(context, outcome_var, effect):
    """
    Perform the causal inference test to see if the difference between the
    control and treatment is as expected.

    :param context: The context
    :type context: behave.context
    :param effect: The expected difference between the control and treatment.
    This test is not likely to pass. It is simply meant to illustrate that it
    is possible to do more than simply "<", "<", and "=".
    :type effect: string
    """
    estimate, (ci_low, ci_high) = run_dowhy(
         "path/to/csv_file.csv",
         "dags/template.dot", # This should be the name of the feature file in "snake case"
         context.treatment_var,
         outcome_var,
         context.control_val,
         context.treatment_val,
         method_name="backdoor.linear_regression") # use whatever estimation method is most appropriate
    assert estimate == float(effect), f"Estimate {estimate} should be {effect}"
