# CauseCumber Skeleton Repository
Computational models are hard to test for several reasons. Their nondeterministic nature means we cannot simply check that a given input configuration produces the expected output, especially since the "expected" output may not be know prior to running the model. Computational models also often have long runtimes and a high computational cost, meaning the number of times the model can be feasibly run is limited.

CauseCumber is a novel testing methodology which combines [Cucumber](https://cucumber.io/) with causal inference (CI) methods to overcome these barriers. The use of CI methods enables computational models to be tested using pre-existing runtime data, potentially reducing the number of times the model needs to be run.

This repository provides a "fill in the gaps" skeleton and a quick start guide to enable you to test your own models. The remainder of the guide breaks down each step and provides a more in depth explanation.

This implementation of CauseCumber is written in python, but this does not mean that your model needs to be. As long as your model can produce a CSV file with rows representing the inputs and columns representing the outputs, this implementation should work for you. Alternatively, both Cucumber and the CI methods upon which CauseCumber is built have supporting libraries in several alternative languages if one of these suits you better.

## Quick Start Setup Guide
1. Clone this repository onto your computer.
        git clone [fixme]
        cd [fixme]
2. Make sure you have Python installed. [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) is a popular choice.
3. Install [Graphviz](https://graphviz.org/) and make sure this is on your path.
4. Install [R studio](https://www.rstudio.com/).
5. Open R studio and install the `dagitty`, `devtools`, and `glue` pagkages.
        install.packages("dagitty")
        install.packages("devtools")
        install.packages("glue")
   Close R studio and return to the terminal.
4. Install the dependencies.
        pip install -r requirements.txt
   NOTE: It is recommended that you can create a [virtual environment](https://docs.python.org/3/library/venv.html) to keep things self contained.
5. Navigate to the `features` directory. Inside is a file called `test.feature` which can be run to see if everything is working as expected.
        cd features
        behave test.feature
   If all is well, you should see the following output.
        Feature: Basic test # test.feature:1

          Scenario: Check everything works       # test.feature:2
            Given The dependencies are installed # steps/test.py:7 0.000s
            When CauseCumber is run              # steps/test.py:11 2.888s
            Then there shouldn't be any errors   # steps/test.py:34 0.000s

        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
    You will also likely see a few messages which start with `R[write to console]`. These are automatically generated and can be safely ignored. If anyone knows how to turn these off, please let me know!

## Fill in the gaps
The `features` directory contains a file `template.feature` which is a "fill in the gaps" template to help you get going with your own model. This file defines in structured natural language the expected behaviour of a hypothetical model. The file begins `Feature: Template`. Here, `Feature:` declares to cucumber that this is a feature file. The name `Template` gives the feature a name. Replace this with something meaningful like "Test my model".

The file then contains a `Background` which lists the names and datatypes of each variable in a table. For inputs, a default value is also provided. Of course, these should be replaced with the variables which apply to the model you are testing.

        Background:
          Given a simulation with parameters
            | parameter | type  | value |
            | input1    | int   | 14    |
            | input2    | str   | hello |
            | input3    | bool  | True  |
          And the following variables are recorded each time step
            | variable | type |
            | output1  | int  |
            | output2  | str  |
            | output3  | bool |

The first `Scenario`, called `Draw DAG` semi-automatically draw a Directed Acyclic Graph showing the causal relationships between the different variables in the background. Further details can be found in the "Causal Graphs" section of this document.

Subsequent Scenarios define tests for the model. These have the following form.

        Scenario: First test
          Given we run the model with {variable}={value1}
          When we run the model with {variable}={value2}
          Then the {output} should be {relationship} control

To write a test, simply substitute in the inputs and values you wish to compare, and declare the expected relationship between the resulting outputs.

The `features/steps` directory contains Python files which tell Cucumber what to do in response to each scenario step. The file `draw_dag.py` contains code which handles the `Draw DAG` scenario in `template.feature`. The remaining scenario steps are defined in `template.py`. The general form of these is quite simple. The `Given` and `When` steps correspond to running the model with a particular input configuration. The `Then` step corresponds to calculating a statistical estimate using causal inference and checking to see if this is as expected.

Another noteworthy file is the `features/environment.py`. Here, you can define hooks to be run before each `Feature`, `Scenario`, or `Tag`. For a full list see the [Behave documentation](https://behave.readthedocs.io/en/stable/tutorial.html#environmental-controls). Using the `@observational` tag before a `Feature` or `Scenario`, we can tell CauseCumber to execute scenarios using pre-existing observational data rather than by running the model specially. This is helpful if you want to be able to switch between the two as you can simply (un)comment the tag in the feature file.

The key aspects here are the `before_tag` method in `environment.py`, which loads the data from the specified filepath and sets the `context.observational` flag to `True` and the `if not context.observational` test in the step definitions in `template.py` which only run the model if we are not using observational data, i.e. we want to get our data by directly running the model.

The remainder of this document breaks down the steps and explains each one in more detail with motivating examples.

## Writing Scenarios
Cucumber tests are expressed as _scenarios_. These describe an execution of a piece of software and the expected outcome using structured natural language. This makes scenarios fairly self explanatory such that they can also serve as additional documentation.

In general, scenarios begin with the keyword `Scenario:` and a the name of the test case. The test case itself is then described using three main keywords:
- The keyword `Given` specifies the _precondition_, i.e. what must hold true before the test case is run.
- The `When` keyword describes the main action of the test case.
- The `Then` keyword, describes the expected outcome.

The `And` keyword can be added after any of the main three keywords to provide additional steps to perform or check.

Groups of scenarios are arranged into `Feature` files, with the `.feature` extension. These begin with the keyword `Feature:` and are given a name. Scenarios are then specified after this, for example:

        Feature: Basic feature
          Scenario: first scenario
            Given...
            When...
            Then...

          Scenario: second scenario
            Given...
            And...
            When...
            And...
            Then...
            And...

Of course, with conventional software, the expected outcome in response to any given input is often known without having to run the software. There is also an assumption that such software is _deterministic_ such that the same input will produce the same output every time. For computational models, neither of these conditions may hold, so we need something more to use Cucumber in this context.

Part of the novelty of CauseCumber is assigning a special meaning to each of the main three keywords which allows computational models to be tested using scenarios. Because the exact output of a model in response to a given input configuration is neither consistent nor known in advance, it is more intuitive to write tests as a comparison of _two_ different runs. For example, we may not know exactly how a model behaves in response to an input `X=7`, we may know that the resulting output should, on average, be less than if we call the same model with input `X=9`. We may even be able to place a bound on how much greater. We could use the following scenario to test this.

        Scenario: Nine should be greater
          Given we run the model with input X=7
          When we run the model with X=9
          Then the output should be greater

Here, we effectively represent two runs of the software in the same scenario. The `Given` keyword describes a _control_ run, and the `When` keyword describes a _treatment_ run. The `Then` keyword describes a comparison between the two with an expected _outcome_. Describing tests in this way is the at the heart of CauseCumber, and is a fairly popular way of tackling the [_oracle problem_](https://ieeexplore.ieee.org/document/6963470) (determining whether the behaviour of a program is acceptable) known as [_metamorphic testing_](https://ieeexplore.ieee.org/document/7422146).

>Note: As with all testing, test cases form a specification for the intended behaviour of the software. It is important to write down in the `Then` step the _expected_ behaviour of the model rather than what _actually_ happens when it is run with the respective outputs. We then check to see if the real behaviour matches what is observed. Scenarios can be trivially constructed by running the model with different inputs and recording relationships between them, however this will not be particularly fruitful in finding faults in the current version of the software since all tests represent _observed_ rather than _intended_ behaviour. Such tests may be useful in finding discrepancies between versions of software (regression testing), but we generally assume that test cases will be written "by hand" as a specification of the intended behaviour rather than a description of how the model actually performs.

For a realistic example, consider [Covasim](https://github.com/InstituteforDiseaseModeling/covasim), a stochastic agent-based simulator for performing COVID-19 analyses. Covasim can be used to explore the potential impact of different interventions, including social distancing, school closures, testing, contact tracing, quarantine, and vaccination. Given that the model was built to predict the outcomes of interventions, even its authors could not reasonably be able to classify a given output as acceptable or not. However, it is very intuitive to say that running the model with, for example, school closures should lead to fewer cases than running it without. To test this, we could write the following scenario.

        Scenario: Test school closures
          Given we run the model without any interventions
          When we run the model with the school closures intervention
          Then there should be fewer infections

Indeed, we would hope that running Covasim with _any_ of the above interventions should lead to fewer cases than with nothing at all, and it would be helpful to test this. Instead of writing six more or less identical scenarios, we could instead use a `Scenario Outline`. This allows us to write a scenario with a placeholder variable. We then specify the values this variable should take in concrete scenarios.

        Scenario Outline: Test interventions
          Given we run the model without any interventions
          When we run the model with the <intervention> intervention
          Then there should be fewer infections
          Examples:
            | intervention      |
            | social distancing |
            | school closures   |
            | testing           |
            | contact tracing   |
            | quarantine        |
            | vaccination       |

Here, `<intervention>` is the placeholder. We then specify its values using the `Examples:` keyword and a table of possible values. The general form of this table is as follows. Each row of the table represents a concrete scenario.

        Examples:
          | variable1 | variable2 | variable3 |...
          | value1    | value2    | value3    |...
          | value1a   | value2a   | value3a   |...

This principle can be applied to any aspect of a scenario. If we also wanted to explore the effects of interventions such as illegal raves or reopening schools, which might _increase_ the number of infections, we could make the relationship a placeholder variable and fill it with `fewer` or `more` as appropriate in the examples table. See `template.feature` for another example.

## Writing Hooks
While scenarios provide an intuitive, human readable way of expressing test cases, Cucumber is not sufficiently smart as to be able to interpret these in the context of running the actual program. To do this, we must manually specify what each step means by writing "hooks". For example, for our above scenarios involving Covasim, we would need to specify what `Given we run the model without any interventions` corresponds actually means. These are placed in a directory called `steps` in the same location as the feature files.

This is the most difficult part of Cucumber testing and can be quite cumbersome. Fortunately, `behave` can be of some help here. If, after writing some scenarios in a file called `tests.feature`, you call `behave test.feature`, it will flag up any steps it comes across without corresponding hooks.

        You can implement step definitions for undefined steps with these snippets:

        @given(u'we run the model without any interventions')
        def step_impl(context):
            raise NotImplementedError(u'STEP: Given we run the model without any interventions')


        @when(u'we run the model with the social distancing intervention')
        def step_impl(context):
            raise NotImplementedError(u'STEP: When we run the model with the social distancing intervention')

These _method stubs_ can be copied and pasted into a file (the name is not important as long as it has the `.py` file extension) within the `steps` directory. Each hook can then be implemented by replacing the `raise NotImplementedError` line with python code to achieve the desired effect. Hooks are python functions which take (at least) one argument, `context`. This allows us to store information for reuse in later steps. It is also possible to add information to the `context` before a scenario is executed, or even before an entire feature file. Further information on this can be found in the [Cucumber docs](https://cucumber.io/docs/cucumber/state/).

While we could implement separate hooks for each intervention, Cucumber allows all of these to be matched by a single hook using a [regular expression](https://cucumber.io/docs/cucumber/cucumber-expressions/). This would capture our chosen intervention as a variable such that we can create a concrete instance of that intervention and pass it to Covasim as part of the input configuration.

## `Then` hooks
The `Given` and `When` hooks are pretty straightforward as they both correspond to running the model. The `Then` hooks are a little more complex as they involve performing a test to see if the two runs of the model relate as expected. It is here that the causal inference side of CauseCumber comes into play.

Because Covasim is nondeterministic, we must run it several times for each intervention and take an average. In the most basic of cases, simply testing whether the average of the control runs relates as expected to the average of the treatment runs may be sufficient, but there are more complex cases where more intelligent methods are required. In our implementation of CauseCumber, we use the doWhy causal inference package to handle all of this for us. The `causecumber_utils.py` file contains a method `run_dowhy` which is called as follows.

        estimate, (ci_low, ci_high) = run_dowhy(
                    data,
                    graph,
                    treatment_var,
                    outcome_var,
                    control_val,
                    treatment_val,
                    method_name)

- `data` is a pandas DataFrame containing the runtime data. This can come either from directly running the program with the specified control and treatment values or from pre-existing runtime data. Each column represents a variable and each row represents a run. All inputs and outputs of interest must be recorded here.
- `graph` is a causal graph as described below. It is critical that there is a direct correspondence between nodes in the graph and columns in the CSV. Each column in the CSV must have a node of the same name in the graph and vice versa.
- `treatment_var` is the name of the variable we are interested in. In the case of our Covasim example, this is `intervention`.
- `outcome_var` is the name of the outcome we are interested in. In our Covasim example, this is the number of infections.
- The `control` and `treatment` values are the values of the `treatment_var` in the `Given` and `When` steps respectively.
- The `method_name` is the name of the dowhy estimation method. This defaults to `backdoor.linear_regression`. Further information can be found in the [dowhy documentation](https://microsoft.github.io/dowhy/dowhy_estimation_methods.html).

The return parameters are as follows:
- `estimate` is the _differential causal estimate_, i.e. the change in the output given the change in the input. For example, if our `control_val` is 20, our `treatment_val` is 40, and the `estimate` is 10, this corresponds to expecting the `outcome_var` to be 10 more when `treatment_var` is 40 than when it is 20.
- `ci_low` and `ci_high` are the _confidence intervals_. These specify a range of values where the causal `estimate` could fall. If zero is in this range, there is either no causal effect or insufficient data to draw a conclusion. The narrower the intervals, the more confident we are in our estimate, although whether the interval is "narrow" or "wide" is open to interpretation.

## Running the Model
While we may only be interested in the effect of one or two variables at a time, computational models often have tens or even hundreds of configuration parameters which are required to actually run the model. When running any software, clearly we need to actually provide all parameters needed for a valid input configuration, not just the ones we're interested in.

To do this, we advocate to use the `Background` feature of cucumber. This may appear at the start of a feature file and typically acts as extra `Given` steps which are applied to every scenario in the file. Here, we use it to specify the names, datatypes, and default values to use for each input required to run the model. We also specify the names and datatypes of the outputs here too, as well as the frequency with which they are reported (for iterative models). When writing hooks to run the model, these values can simply be extracted by iterating the rows of `context.table`. An example of this can be seen in `features/covasim_dag.feature`.

        Background:
          Given a simulation with parameters
            | parameter     | value      | type |
            | quar_period   | 14         | int  |
            | n_days        | 84         | int  |
            | pop_type      | hybrid     | str  |
            | pop_size      | 50000      | int  |
            | pop_infected  | 100        | int  |
            | location      | UK         | str  |
            | interventions | baseline   | str  |
          And the following variables are recorded weekly
            | variable          | type |
            | cum_tests         | int  |
            | n_quarantined     | int  |
            | n_exposed         | int  |
            | cum_infections    | int  |
            | cum_symptomatic   | int  |
            | cum_severe        | int  |
            | cum_critical      | int  |
            | cum_deaths        | int  |

For a given scenario, the provided control and treatment values specified in the `Given` and `When` steps can then overwrite the default values when running the model. The result should be a CSV file or pandas `DataFrame` in the appropriate format which can be passed to `run_dowhy` as the `data` parameter.

## Observational Data
Because of their long runtimes, it may not always be possible to run the model for each scenario, especially if multiple repeats are required to account for nondeterminism. Instead, CauseCumber can work with observational data to estimate how the model might perform under the given control and treatment values. This is, in essence, the same process as above, except that the model is run in advance and the resulting CSV is passed to `run_dowhy` instead of one resulting from running the model with only the parameters of interest.

It is also worth noting here that the use of observational data allows the testing of scenarios which would be impossible to test by running the model. For example, Covasim records the cumulative number of critical cases and cumulative deaths every time step. These are both stochastic outputs, so we cannot set them directly, but they are related. By using observational data, we can test that this relationship is as expected.

## Causal Graphs
Causal graphs are an essential part of most modern CI techniques. They are used to encode assumptions about the dependencies between different variables. Causal graphs are made up of _nodes_ and _edges_ where nodes represent variables (inputs and outputs) and edges represent direct causality such that an edge `X -> Y` means "X causes Y".

Causal graphs must be _acyclic_. That is, we cannot have a path `X -> Y ... -> X` such that `X` is, in a way, a cause of itself. Many computational modes are iterative, with outputs changing over time. Here, the different variable values at each time step must be represented by a separate variable in the causal graph. For example, if our model outputs a variable _Y_ over 5 time steps, we would have variables `Y_1...Y_5` in the causal graph.
Because of the repetitive nature of computational models, it is often the case that, once initialised, the causal graph has the same _repeating structure_ each iteration.

Drawing causal graphs is, in principle, as simple as creating a node for each variable and connecting them as appropriate. For simple models, this may simply be a fan-like structure in which each each input feeds into the output. For more complex models, especially those which vary over time, the different inputs and outputs may be connected in more complex ways.

The `causecumber_utils` file provides several methods which can be used to help draw causal graphs. For simpler models, the `draw_connected_dag` method can be used. This takes two arguments, a list of input names and a list of output names, and returns a connected graph in which each input causes each output and each output causes every other output. This connected structure will likely contain cycles, but edges for which there is known to be causality can then be pruned manually. Unfortunately, due to the nature of causal graphs, there is no way to automate this step.

For iterative models where outputs change over time, the `draw_connected_repeating_unit` can be used to draw a similar connected structure. This also takes a list of inputs (which are static) and a list of outputs (which evolve over time). It returns a connected structure as above which represents the time step n to n+1. Again, edges will need to be pruned. The repeating unit can then be iterated arbitrarily using the `iterate_repeating_unit` method, which takes the repeating unit and a number of steps to iterate for. This is the number of time steps the model was run for.

Because of the complex nature of causal graphs and the fact that they encode our assumptions, there is no way to fully automate the process of drawing them. There must always be some human interaction here. The file `features/covasim_dag.feature` and its corresponding step definitions in `steps`, show an example of how to draw a dag semi-automatically using the helper functions and the `Background` table, which lists the names and types of the model inputs and outputs. These are transformed into a connected repeating structure, edges pruned, and the resulting structure iterated.

In addition to pruning edges, it may be necessary to manually add some, for example to represent causal connections between inputs. Given the examples within `steps/covasim_dag.py`, this should be fairly straightforward.
