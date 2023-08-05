from cellnopt.data import cnodata, plotting


def test_plotting():
    plotting.plotdata(cnodata("PKN-ToyPB.sif"),cnodata("MD-ToyPB.csv"), "ToyPB")

