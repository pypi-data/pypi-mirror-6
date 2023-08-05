Feature: Asynchronous Testing
  In order to test event-based applications with fresher 
  As a developer and fresher user
  I want to be able to execute tests that return their results asynchronously

  # This scenario requires twisted to work correctly
  # otherwise it will (and should) not pass.
  Scenario: Event-based testing
    When I implement a step that returns a twisted Deferred object
    Then fresher will wait for the result before executing the next step

