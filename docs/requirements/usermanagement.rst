============================
User Management Requirements
============================

* Each **User** must authenticate in order to work with the system. The
  authentication process is called **Login**
* **Anonymous user** (i.e. user who did not authenticate) can only access
  public pages.

Access Priviledges
------------------

**Users** have certain **access privileges**. Based on that privileges
certain information is available or certain action can be executed.
The **access privileges** are bundled into named **Roles**.
Each user can get assigned exactly one **Role**.

* There is a default **Role** named *SiteAdmin*. A user who has that role
  is able to access all information and to execute every possible action.
* There is a default having the username *admin*, who gets assigned the
  *SiteAdmin* role. (This assures, that the applications is kept manageable.)

User Profile Data
-----------------

Associated with a **User** is some profile data:

* First name
* Last name
* Email address

User Management Requirements
============================

Self Management
---------------

All **Users** have the ability to:

* Self-register
* Update own profile data
* Terminate the **User** account
* Review their **Activities**

User Management
---------------

**Users** who have appropriate **access privileges** can:

* Activate/Deactivate other **Users**
* Create and delete a **User** account (delete is equivalent to terminate)
* Update profile data of a **User**
* Assign a **Role** to a **User**
* Review **Activities** of a **User**

