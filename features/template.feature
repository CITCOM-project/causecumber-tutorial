# Uncomment to run the scenarios using observational data rather than by executing the model.
# @observational("path_to_csv_file.csv")

Feature: Template # replace with something nore meaningful

  Background:
    Given a simulation with parameters
      # Put the name, datatype, and default value of your model inputs here
      # All python basic types are supported automatically
      # More complex types and custom data structures will need manual conversion
      # input1 is an integer with default value 14
      # input2 is a string with default value "hello"
      # input3 is a boolean with default value True
      | parameter | type  | value |
      | input1    | int   | 14    |
      | input2    | str   | hello |
      | input3    | bool  | True  |
    And the following variables are recorded each time step
      # Put the name and datatype of your output parameters here
      # output1 is an integer
      # output2 is a string
      # output3 is a bool
      | variable | type |
      | output1  | int  |
      | output2  | str  |
      | output3  | bool |

  # This scenario draws the causal DAG, which is used by doWhy in the estimation
  # of the causal effect. It is not a test for the model. The default behaviour
  # is to connect every input to every output and all the outputs at time n are
  # connected to every output at time n+1.
  # Causal DAGs must be acyclic, so edges must be pruned to make this the case.
  Scenario: Draw DAG # The actual name doesn't matter
    Given a connected repeating unit
    When we prune the following edges
      # Put the edges for which s1 is known not to cause s2
      # Outputs at time step n have suffix _n
      # Outputs at time step n+1 have suffix _n+1
      | s1        | s2         |
      | input1    | output2_n  |
      | output1_n | output2_n1 |
    And we add the following edges
      # Put in any edges where you want to explicitly add causality where it
      # does not appear by default, for example between inputs.
      | s1     | s2     |
      | input1 | input2 |
    # replace 12 with however many time steps you want
    Then we obtain the causal DAG for 12 time steps

  # The actual tests occur from this point onwards

  Scenario: First test # Call it something sensible
    # Define the control conditions - replace "input1" with one of the inputs from the Background and give it a default value
    Given we run the model with input1=50000
    # Define the treatment conditions - replace "input1" with the same input as the previous step and give it a different value
    When we run the model with input1=100000
    # Define the expected behaviour - replace "output2" with one of the outputs from the background and give a relationship between the control and treatment conditions
    # You could also define a range, function of the control, or an exact value
    Then the output2 should be > control

  # This is an example with testing a concrete value for the estimate
  # Note that we test the _effect_ rather than the actual value of output3
  Scenario: Example of an exact value
    Given we run the model with input3=True
    When we run the model with input3=False
    Then the effect on output3 should be 0

  # Scenario outlines allow us to specify a template which is then populated
  # into several concrete scenarios.
  # Placeholder variables are enclosed in tags <...>
  Scenario Outline: Test lots of things
    Given we run the model with input2=<control>
    When we run the model with input2=<treatment>
    Then the output1 should be <relationship> control
    # Use the Examples table to specify concrete values for each placeholder
    # Each row represents a concrete scenario
    Examples:
      | control | treatment | relationship |
      | hello   | world     | =            |
      | top     | taste     | >            |
      | lala    | la        | <            |
