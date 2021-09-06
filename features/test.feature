Feature: Basic test
  Scenario: Check everything works
    Given The dependencies are installed
    When CauseCumber is run
    Then there shouldn't be any errors
