.. _lots_workflow:

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
            "verification" -> "active.salable";
            edge[style=dashed];
            "active.salable" -> "dissolved";
            edge[style=solid];
            "active.salable" -> "active.awaiting";
            edge[style=solid];
            "active.awaiting" -> "active.salable";
            edge[style=solid];
            "active.awaiting" -> "active.auction";
            edge[style=solid];
            "active.auction" -> "sold";
    }


Legend
--------

   * dashed line - user action
    
   * solid line - action is done automatically
