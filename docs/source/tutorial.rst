.. _tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `lots` endpoint:


Just invoking it reveals empty set.

Now let's attempt creating a lot:


Error states that the only accepted Content-Type is `application/json`.

Let's satisfy the Content-type requirement:


Error states that no `data` has been found in JSON body.


.. index:: Lot

Creating lot
--------------


Let's create lot with the minimal (only required) data set:


Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created lot: its internal
`id` (that matches the `Location` segment), its official `lotID` and
`dateModified` datestamp stating the moment in time when lot was last
modified. Pay attention to the `lotType`. Note that lot is
created with `pending` status.

Let's access the URL of the created object (the `Location` header of the response):


.. XXX body is empty for some reason (printf fails)

We can see the same response we got after creating lot.

Let's see what listing of lots reveals us:


We do see the internal `id` of the lot (that can be used to construct full URL by prepending `https://lb.api-sandbox.registry.ea.openprocurement.net/api/0.1/lots/`) and its `dateModified` datestamp.

The previous lot contained only required fields. Let's try creating lot with more data
(lot has status `created`):


And again we have `201 Created` response code, `Location` header and body with extra `id`, `lotID`, and `dateModified` properties.

Let's check what lot registry contains:


And indeed we have 2 lots now.

Modifying Lot
---------------

Let's update lot description:


.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing loy data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:


Deleting Lot
--------------

Let's delete lot:



Integration with assets
---------------------



