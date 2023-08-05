from cellnopt.data import cnodata, CNOData
import os
import shutil

def test_cnodata():
    c = cnodata()
    filename = cnodata("PKN-ToyMMB.sif", local=False)
    available_files = cnodata()



def test_CNOdata():
    c = CNOData()
    c.package_data
    c.cnodata("ToyMMB.sif", local=False)
    print(c)
    c.check()
    c.directories


    # test aliases
    c.cnodata("ToyModelMMB.sif", local=False)


    
    filename = c.cnodata("PKN-ToyMMB.sif", local=False)
    shutil.copy(filename, "test.sif")
    c.cnodata("test.sif", local=True)
    os.remove("test.sif")


