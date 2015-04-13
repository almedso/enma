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
We rather measure the covererage and make a cace by case decision if
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
Ideally the business cases/ scnearios/use cases are described and test cases
are aligned along.

Behavior tests follow a Given, When, Then structure wherey When Then might be
be repeated. Given also might be another (successful) test case. E.g. user has
logged on.

Subject of tests are at least:

* Fragments of business processes
* Complete business processes

Database preparation
....................

We use fixtures as well as specific preparators.

* Cover as much as necessary by functional tests

Test Specification for manual Tests
===================================

* User successfully logs in using an OpenId provider

  * Use google (fails because it is deprecated -> moved to OAuth2)
  * Use yahoo
  * Use flickr
