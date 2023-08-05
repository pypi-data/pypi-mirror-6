import pylab


# this should not be a public function. This is used only for the plotting
# inside the documentation.
__all__ =[]


def plotdata(model, data, filename, subfield=False):
    # should be inside the function to that cellnopt.data does not depend on
    # cellnopt.core. Should be used for the documentation only.
    from cellnopt.core import *
    
    c = CNOGraph(model, data)
    c.plotdot(filename=filename+".svg", remove_dot=False, show=False)

    # now png with high resolution of the original model/data
    c.graph['graph'] = {"splines":True, "size":(20,20), "dpi":200}
    c.plotdot(filename=filename+".png", remove_dot=False, show=False)
    pylab.figure(1, dpi=144)
    pylab.subplot(2,2,1)
    pylab.imshow(pylab.imread("%s.png" % filename))
    pylab.axis("off")
    pylab.title("PKN model")

    # the original model with compressed nodes highlighted
    c.preprocessing(expansion=False)
    c._compressed = c.compressable_nodes[:] # do not compress but set node attribute of node that are compressable
    c.plotdot(filename=filename+"_comp_1.png", remove_dot=False, show=False)
    pylab.subplot(2,2,2)
    pylab.imshow(pylab.imread("%s_comp_1.png" % filename))
    pylab.axis("off")
    pylab.title("Annotated PKN model")

    # the compressed nodes
    c.plotdot(filename=filename+"_comp_2.png", remove_dot=False, show=False)
    pylab.subplot(2,2,3)
    pylab.imshow(pylab.imread("%s_comp_2.png" % filename))
    pylab.axis("off")
    pylab.title("Compressed model")

    # the compressed and expanded model
    c.preprocessing()
    c.plotdot(filename=filename+"_comp_expanded.png", remove_dot=False, show=False)
    pylab.subplot(2,2,4)
    pylab.imshow(pylab.imread("%s_comp_expanded.png" % filename))
    pylab.axis("off")
    pylab.title("Compressed and expanded model")
