=======
Testing
=======

Testing Strategy
================

Unit Tests
----------

The goals is to achieve 100 percent test coverage.
Ideally, every path should be followed at least by one test case.
Sometimes (for configiguration or similar this does not make sense and will
not enforced.
We rather measure the coverage and make a case by case decision if
the specific coverage is to low.

Subject of tests are at least:

* Models and their logic
* Domain functionality
* Forms
* Views as well

Behavior Tests
--------------

This is the same as functional testing.
The goal is to cover all relevant business processes.
Ideally the business cases/ scenarios/use cases are described and test cases
are aligned along.

Behavior tests follow a Given, When, Then structure, whereby When Then might be
be repeated. Given also might be another (successful) test case. E.g. user has
logged on.

Subject of tests are at least:

* Fragments of business processes
* Complete business processes

Database preparation
....................

We use fixtures as well as specific preparer.

* Cover as much as necessary by functional tests

