.. _ExtLiverPCB:



ExtLiverPCB
=============


.. topic:: Description

    .. include:: ../../share/data/ExtLiverPCB/description.txt



Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the NORMALISED share/data, click on the following link :download:`download share/data   <../../share/data/ExtLiverPCB/MD-ExtLiverPCB.csv>`.
* To download the model, click on the following link :download:`download model  <../../share/data/ExtLiverPCB/PKN-ExtLiverPCB.sif>`.



PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cellnopt.misc import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ExtLiverPCB.sif"),cnodata("MD-ExtLiverPCB.csv"),"ExtLiverPCB")

Here below is a high resolution SVG pictures of the PKN model. 

.. _ExtLiver_highres:

.. graphviz:: ExtLiverPCB.dot


.. CNOlist view
   ~~~~~~~~~~~~~~~

.. .. plot::
    :width: 40%
    :include-source:

..    from cellnopt.misc import *
    from sampleModels.tools import get_share/data
    share/data = readMidas(get_share/data("ExtLiverPCB.csv"))
    cnolist = makeCNOlist(share/data)
    plotValueSignals(cnolist)


.. .. graphviz:: ../ExtLiverPCB.dot
