# data_model/test
## Testers
This folder contains a number of Mephisto Data Model "test benches", which serve to be the standard tests that Mephisto Abstractions need to be able to pass in order for the system to be able to use them. As such, they define a number of tests, and then new classes can be tested against the bench by making a subclass that implements the required setup functions. See the `test/server/architects/test_heroku_architect` implementation for an example.

## Utils
Any utility functions that can be used for creating useful mocks, DB setups, or other such prerequisites for a test.
