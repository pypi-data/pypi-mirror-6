
.. _ToyMMB_T2:

ToyMMB_T2
================


.. topic:: Description

    .. include:: ../../share/data/ToyMMB_T2/description.txt




Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the data, click on the following link :download:`download data   <../../share/data/ToyMMB_T2/MD-ToyMMB_T2.csv>`
* To download the model, click on the following link :download:`download model  <../../share/data/ToyMMB_T2/PKN-ToyMMB_T2.sif>`



PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cellnopt.misc import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ToyMMB_T2.sif"), cnodata("MD-ToyMMB_T2.csv"),"ToyMMB_T2")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _ToyMMB_T2_highres:

.. graphviz:: ToyMMB_T2.dot
    


.. CNOlist view
   ~~~~~~~~~~~~~~~

..    .. plot::
        :width: 40%
        :include-source:

..    from cellnopt.misc import *
    from sampleModels.tools import get_data
    data = readMidas(get_data("ToyMMB_T2.csv"))
    cnolist = makeCNOlist(data)
    plotValueSignals(cnolist)
