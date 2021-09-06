Feature: Compare interventions
  Background:
    Given a covasim simulation with parameters
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

  # TODO: this is a bit clunky. It might not be  reasonable to assume that a
  # domain expert would be able to list all edges that wouldn’t be present
  # before seeing the connected graph
  Scenario: Draw DAG
    Given a connected repeating unit
    When we prune the following edges
      | s1                | s2                 |
      | quar_period       | n_exposed_n        |
      | quar_period       | cum_infections_n   |
      | quar_period       | cum_symptomatic_n  |
      | quar_period       | cum_severe_n       |
      | quar_period       | cum_critical_n     |
      | quar_period       | cum_deaths_n       |
      | quar_period       | cum_tests_n        |
      | interventions     | cum_infections_n   |
      | interventions     | cum_symptomatic_n  |
      | interventions     | cum_severe_n       |
      | interventions     | cum_critical_n     |
      | interventions     | cum_deaths_n       |
      | pop_type          | cum_deaths_n       |
      | pop_type          | cum_tests_n        |
      | pop_size          | cum_deaths_n       |
      | pop_size          | cum_tests_n        |
      | location          | cum_deaths_n       |
      | location          | cum_tests_n        |
      | pop_infected      | n_quarantined_n    |
      | pop_infected      | n_exposed_n        |
      | pop_infected      | cum_deaths_n       |
      | pop_infected      | cum_tests_n        |
      | n_days            | n_quarantined_n    |
      | n_days            | n_exposed_n        |
      | n_days            | cum_infections_n   |
      | n_days            | cum_symptomatic_n  |
      | n_days            | cum_severe_n       |
      | n_days            | cum_critical_n     |
      | n_days            | cum_deaths_n       |
      | n_days            | cum_tests_n        |
      | n_quarantined_n   | cum_infections_n1  |
      | n_quarantined_n   | cum_symptomatic_n1 |
      | n_quarantined_n   | cum_severe_n1      |
      | n_quarantined_n   | cum_critical_n1    |
      | n_quarantined_n   | cum_tests_n1       |
      | n_quarantined_n   | cum_deaths_n1      |
      | n_exposed_n       | n_quarantined_n1   |
      | n_exposed_n       | cum_symptomatic_n1 |
      | n_exposed_n       | cum_severe_n1      |
      | n_exposed_n       | cum_critical_n1    |
      | n_exposed_n       | cum_deaths_n1      |
      | n_exposed_n       | cum_tests_n1       |
      | cum_infections_n  | cum_severe_n1      |
      | cum_infections_n  | cum_critical_n1    |
      | cum_infections_n  | cum_deaths_n1      |
      | cum_infections_n  | cum_tests_n1       |
      | cum_symptomatic_n | n_exposed_n1       |
      | cum_symptomatic_n | cum_critical_n1    |
      | cum_symptomatic_n | cum_deaths_n1      |
      | cum_symptomatic_n | cum_tests_n1       |
      | cum_severe_n      | n_quarantined_n1   |
      | cum_severe_n      | n_exposed_n1       |
      | cum_severe_n      | cum_infections_n1  |
      | cum_severe_n      | cum_symptomatic_n1 |
      | cum_severe_n      | cum_tests_n1       |
      | cum_severe_n      | cum_deaths_n1      |
      | cum_critical_n    | n_quarantined_n1   |
      | cum_critical_n    | n_exposed_n1       |
      | cum_critical_n    | cum_infections_n1  |
      | cum_critical_n    | cum_symptomatic_n1 |
      | cum_critical_n    | cum_severe_n1      |
      | cum_critical_n    | cum_tests_n1       |
      | cum_tests_n       | n_exposed_n1       |
      | cum_tests_n       | cum_infections_n1  |
      | cum_tests_n       | cum_symptomatic_n1 |
      | cum_tests_n       | cum_severe_n1      |
      | cum_tests_n       | cum_critical_n1    |
      | cum_tests_n       | cum_deaths_n1      |
      | cum_deaths_n      | n_quarantined_n1   |
      | cum_deaths_n      | cum_infections_n1  |
      | cum_deaths_n      | cum_symptomatic_n1 |
      | cum_deaths_n      | cum_severe_n1      |
      | cum_deaths_n      | cum_critical_n1    |
    Then we obtain the causal DAG for 12 weeks

  Scenario Outline: Test and trace
