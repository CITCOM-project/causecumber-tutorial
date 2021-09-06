
def before_feature(context, feature):
    """
    Run before each feature to, for example, set up key state variables.

    :param context: The Cucumber context
    :type context: behave.Context
    :param feature: The feature
    :type feature: behave.Feature
    """
    context.params_dict = {} # The input parameters
    context.types = {} # The datatype of each variable
    context.feature_name = context.feature.name.replace(" ", "_").lower()
    context.dag_path = f"dags/{context.feature_name}.dot" # Where to save the causal DAG
    context.observational = False # Are we using observational data? Tag with @observational("path_to_csv_file.csv") to make it so


# This allows you to tell CauseCumber to use observational data.
# To do this simply tag a Feature or Scenario with @observational('path/to/csv_file.csv')
# You will also need to add a corresponding `if` statement in your step file
# to test if `context.data` exists before running the model.
def before_tag(context, tag):
    """
    Run before each tag to, for example, set up key state variables.

    :param context: The Cucumber context
    :type context: behave.Context
    :param feature: The feature
    :type feature: behave.Feature
    """
    obs_tag_re = re.compile('observational\(("|\')(.+)("|\')\)')
    obs_match = obs_tag_re.match(tag)
    if obs_match:
        context.data = pd.read_csv(obs_match.group(2))
        context.observational = True # We're using observational data
