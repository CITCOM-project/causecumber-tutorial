import sys
sys.path.append("../") # This one's for running `behave` in `features`

from causcumber_utils import *


@given(u'The dependencies are installed')
def step_impl(context):
    """
    If we have got to running this method, all the dependencies should be installed.
    
    :param context: The context
    :type context: behave.Context
    """
    pass

@when(u'CauseCumber is run')
def step_impl(context):
    """
    Run doWhy with some sample data just to check it's installed and working.
    
    :param context: The context
    :type context: behave.Context
    """
    import dowhy.datasets

    # Load some sample data
    data = dowhy.datasets.linear_dataset(
        beta=10,
        num_common_causes=5,
        num_instruments=2,
        num_samples=10000,
        treatment_is_binary=True)

    estimate, (ci_low, ci_high) = run_dowhy(
              data=data['df'],
              graph=data["dot_graph"],
              treatment_var=data["treatment_name"],
              outcome_var=data["outcome_name"],
              control_val=0,
              treatment_val=1,
              method_name="backdoor.linear_regression",
              dump_adj=False)


@then(u'there shouldn\'t be any errors')
def step_impl(context):
    """
    If we've got this far, then we've won.
    
    :param context: The context
    :type context: behave.Context
    """
    pass
