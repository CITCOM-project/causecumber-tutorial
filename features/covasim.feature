Feature: Covasim basic example

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
