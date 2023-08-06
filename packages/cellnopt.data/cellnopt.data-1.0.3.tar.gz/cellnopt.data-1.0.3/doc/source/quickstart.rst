.. _quickstart:

Retrieve the path to a data or model file
##################################################




The following code should return a path to a temporary file corresponding to the
requested filename::

    from cellnopt.data import cnodata
    temp_filename = cnodata("PKN-ToyPCB.sif")

that can be used later on. For instance with :ref:`cellnopt.core.sif`::

    from cellnopt.core import SIF
    s = SIF(temp_filename)


.. seealso:: `cellnopt.data page <http://www.ebi.ac.uk/~cokelaer/cellnopt.data//>`_ 

**cellnopt.data** main objective is to ease the access to data hence the unique
function :func:`cnodata`. 

Here are the steps follows by cnodata:

    #. tries in the local directory (not very useful... but in case it is already there.)
    #. tries to find the file in the cellnopt.data package itself, which is locally installed. 

