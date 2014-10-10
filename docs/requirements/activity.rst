=============================
Activity Recording and Access
=============================

Business, or security relevant action or **Activity** is recorded for the
purpose of post mortem analysis what was done when by whom.

Recorded Activity Entry
-----------------------

Timestamp:
   When did something happen.
Actor:
   The **User** who did the action
Category:
   An activity category like *Authentication*, *Privilege*, *User*
Description:
   Short description of what happened
Acted_on:
   The **User** whose data was modified (optional)
Origin:
   Which IP address did this request came from (optional)

Review Activity Log
-------------------

* Every **User** can see his/her own activities.
* User who have the **access privilege** to read the complete activity log
  review all **activity** entries.
