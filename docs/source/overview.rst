Overview
========

openregistry.lots.basic contains the description of the Registry Data Base.

Features
--------

* Lots are formed by DGF.
* Several assets (or the one only) may be included in one lot.
* Assets which are included in lot, will be marked as attached to it, after that lot is finally formed.
* In case of at least one asset, which is going to be included in a lot, has 
  already been attached to another one, such a lot will be marked as invalid.
* After lot has been successfully created, it becomes available for auction.


Conventions
-----------

API accepts `JSON <http://json.org/>`_ or form-encoded content in
requests.  It returns JSON content in all of its responses, including
errors.  Only the UTF-8 character encoding is supported for both requests
and responses.

All API POST and PUT requests expect a top-level object with a single
element in it named `data`.  Successful responses will mirror this format. 
The data element should itself be an object, containing the parameters for
the request.

If the request was successful, we will get a response code of `201`
indicating the object was created.  That response will have a data field at
its top level, which will contain complete information on the new auction,
including its ID.

If something went wrong during the request, we'll get a different status
code and the JSON returned will have an `errors` field at the top level
containing a list of problems.  We look at the first one and print out its
message.

---------------------

Project status
--------------

The project has pre alpha status.

The source repository for this project is on GitHub: 
https://github.com/openprocurement/openregistry.api  

Documentation of related packages
---------------------------------

* `OpenProcurement API <http://api-docs.openprocurement.org/en/latest/>`_

API stability
-------------

API is relatively stable. The changes in the API are communicated via `Open Procurement API
<https://groups.google.com/group/open-procurement-api>`_ maillist.


Next steps
----------
You might find it helpful to look at the :ref:`tutorial`.
