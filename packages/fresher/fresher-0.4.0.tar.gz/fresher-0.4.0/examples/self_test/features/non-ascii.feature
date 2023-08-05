Feature: Non-ascii

  Scenario: Non-ascii
    Given un éléphant dit "hélas"

  Scenario: Non-ascii failure
    Then échoue
