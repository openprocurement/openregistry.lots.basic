.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: basicLot 

.. _lot:

Basic Lot
===============

Schema
------

:id:
    string, auto-generated, read-only
    
:lotID:
   string, auto-generated, read-only

   The lot identifier to refer that lot to in the `paper` documentation. 

   |ocdsDescription|
   LotID is included to make the flattened data structure more convenient.
   
:date:
    string, auto-generated, read-only
    
    The date of lot creation/undoing.
    
:dateModified:    
    string, auto-generated, read-only
    
    |ocdsDescription|
    Date when the lot was last modified.
    
:status:
    string, required
    
    The lot status within the Registry.
    
:value:
    :ref:`Value`, required 
    
    Estimated lot value.

:assets:
    string, optional
    
    ID of the related basic asset.
    
:lotType:
    string, required

    Type of the given lot.

:title:
    string, multilingual
    
    * Ukrainian by default (required) - Ukrainian title
    
    * ``title_en`` (English) - English title
    
    * ``title_ru`` (Russian) - Russian title
    
    Oprionally can be mentioned in English/Russian.
    
:description:
    string, multilingual, optional
    
    |ocdsDescription|
    A description of the goods, services to be provided.
    
    * Ukrainian by default - Ukrainian decription
    
    * ``decription_en`` (English) - English decription
    
    * ``decription_ru`` (Russian) - Russian decription
    
:documents:
    
    |ocdsDescription|
    All related documents and attachments.
    
:lotCustodian:
   :ref:`Organization`, required

   An entity managing the lot.

:mode:
    optional
    
    The additional parameter with a value ``test``.
    
Lots Workflow
==============

.. graphviz::

    digraph G {
            node [style=filled, color=lightgrey];
            edge[style=dashed];
            "draft" -> "pending";
            edge[style=dashed]
            "pending" -> "deleted";
            edge[style=dashed];
            "pending" -> "verification";
            edge[style=solid];
            "verification" -> "pending";
            edge[style=solid];
            "verification" -> "active.saleable";
            edge[style=dashed];
            "active.saleable" -> "dissolved";
            edge[style=solid];
            "active.saleable" -> "active.awaiting";
            edge[style=solid];
            "active.awaiting" -> "active.saleable";
            edge[style=solid];
            "active.awaiting" -> "active.auction";
            edge[style=solid];
            "active.auction" -> "sold";
    }


Legend
--------

   * dashed line - user action
    
   * solid line - action is done automatically
    
.. _value:

Value
===============

Schema
------

:amount:    
    float, required

    Should be positive.
    
:currency:
    string, required
    
    |ocdsDescription|
    The currency in 3-letter ISO 4217 format.
    
:valueAddedTaxIncluded:
    bool, required

