Feature: JSON Schema Builder and Annotator

  Scenario: Generate JSON Schema from JSON file
    Given I have a JSON file named "example.json"
    When I run the JSON Schema Builder and Annotator
    And I selected the TUI option
    Then I should see a table with the properties of the schema and their absolute paths
    And there should be no errors in the console
    And I should be able to add annotations to the schema
    And I should be able to see an updated table with the annotations
    And there should be no errors in the console
    And I should be able to filter the schema by path
    And there should be no errors in the console
    And I should be able to save the schema to a file
    And there should be no errors in the console