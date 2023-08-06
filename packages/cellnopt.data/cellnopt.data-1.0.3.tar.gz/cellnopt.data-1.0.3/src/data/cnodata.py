import os
import easydev
from easydev import get_shared_directories

__all__ = ["cnodata", "build_filepaths", "CNOData", "lookfor"]

def build_filepaths():
    "returns a dictionary containing SIF/CSV files found in the share directory"
    datadirs = get_shared_directories("cellnopt.data", "data")
    filepaths = {}
    for d in datadirs:
        name = os.path.split(d)[1]
        for filename in os.listdir(d):
            ext = os.path.splitext(filename)[1]
            if ext in [".csv", ".CSV", ".SIF", ".sif"]:
                # is there an aliases.py file to get aliases from ?
                try:
                    exec(open(d + os.sep + "aliases.py","r").read())
                    aliases[filename]
                except:
                    # if not, let us jsut fill the aliases with an empty list
                    aliases = {filename:[]}
                filepaths[filename] = {
                    'path':d+os.sep+filename,
                    'name':name,
                    'origin':'cellnopt.data',
                    'aliases': aliases[filename]}
    return filepaths


def cnodata(filename=None, local=False):
    """Get path of a model or MIDAS file contained in **cellnopt.data** package

    :param str filename: if not provided, cnodata returns the existing files in
        cellnopt.data share/data directory. Otherwise, returns the path of
        filename if found. If not found, print possible similar filenames using
        :func:`lookfor`
    :param bool local: look only in the local directory (default is False)

    :: 

        from cellnopt.data import cnodata
        filename = cnodata("PKN-ToyMMB.sif")
        filename = cnodata("PKN-ToyMMB.sif", local=True)
        available_files = cnodata()

    .. seealso:: :ref:`CNOData`, :ref:`lookfor`.


    """
    if filename != None:
        return lookfor(filename, local=local)
    else:
        print(easydev.underline("Valid names are:"))
        c = CNOData(verbose=False)
        for k in sorted(c.package_data.keys()):
            print k
        return sorted(c.package_data.keys())


def lookfor(filename, local=False):
    """Lookfor a filename 

    :param str filename: a filename to lookfor in cnodata database
    :return: nothing

    If found exactly, return filename. Otherwise, prints filenames found in the
    database that ressembles the input filename.

    """
    c = CNOData(verbose=False)
    p = c.cnodata(filename, local=local)
    if p ==None:
        for k in sorted(c.package_data.keys()):
            if filename.lower() == k.lower():
                print("Maybe you meant: %s" %k)
            if filename.lower() in  k.lower():
                print("Maybe you meant: %s" %k)
    else:
        return p


class CNOData(object):
    """class to ease manipulation of the shared directories to retrieve data

    ::

        from cellnopt.data import CNOData
        c = CNOData()
        c.package_data
        c.cnodata("ToyMMB.sif")

    """
    def __init__(self, verbose=True, web=False):

        self.package_data = build_filepaths()
        self.verbose = verbose
        self.check()

    def _get_directories(self):
        directories = set([v['name'] for k,v in self.package_data.iteritems()])
        return sorted(directories)
    directories = property(_get_directories, doc="return directories found in share/data")

    def _get_aliases(self):
        aliases = []
        for k, v in self.package_data.iteritems():
            for a in self.package_data[k]['aliases']:
                aliases.append(a)
        return aliases
    aliases = property(_get_aliases, doc="returns known aliases")

    def _get_filenames(self):
        filenames = self.package_data.keys()
        return filenames
    filenames = property(_get_filenames, "return relevant model and data filenames")

    def check(self):
        """check that aliases are unique

        """
        #aliases must not be found in keys
        aliases = self.aliases
        if len(set(aliases)) == len(aliases):
            return
        else:
            raise Exception("aliases duplication found. This must not happen. check package_data attribute")

    def cnodata(self, filename, local=True):
        """Returns path of a filename (if found)"""
        # if local is true, we first want to try that option
        if local == True:
            if os.path.exists(filename):
                return filename
            else:
                raise IOError("filename %s not found in local directory" % filename)

        if filename in self.filenames:
            return self.package_data[filename]['path']
        elif filename in self.aliases:
            if self.verbose:
                print("%s not found in cellnopt.data directories. Checking for aliases" % filename)
            for k, v in self.package_data.iteritems():
                if filename in self.package_data[k]['aliases']:
                    print("%s is an alias of %s. Please use the latter filename." % (filename, k))
                    return self.package_data[k]['path']
        # now, if loca was false, we cannot be here. 
        # in addition, if filename not found in the pacakge, we can still try to
        # get here from the local directory !
        if os.path.exists(filename):
            return filename

        # finally, nothing found, shall we raise a warning ? error?
        if self.verbose:
            print("%s not found in cellnopt.data" % filename)
        return

    def __str__(self):
        txt = ""
        dirs = sorted(self.package_data.keys())
        for d in dirs:
            txt += easydev.underline(d) + "\n"
            txt += " origin:"+ self.package_data[d]['name'] + "\n"
            txt += " aliases:"+ ", ".join([x for x in self.package_data[d]['aliases']]) + "\n"
            txt += " path:"+ self.package_data[d]['path'] + "\n"
            txt += "\n"
        return txt




