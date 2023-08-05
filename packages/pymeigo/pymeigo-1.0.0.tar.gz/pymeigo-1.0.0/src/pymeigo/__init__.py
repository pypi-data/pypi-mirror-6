import pkg_resources

#__all__ = ["version", "info"]


try:
    version = pkg_resources.require("pymeigo")[0].version
except:
    version = ""

def info():
    print("MEIGO python interface (pymeigo)")
    print("version: %s" % version)
    from rtools import RPackage
    status = RPackage("MEIGOR", require="0.9.6")
    if status.package:
        print("linked to MEIGOR R version : %s" % status.version)
    else:
        print("MEIGOR R package could not be loaded")

# load the R package. If not possible, tries to install it
import init
init.install()

import wrapper_meigo
from wrapper_meigo import *

import funcs
from funcs import *

import meigo
from meigo import *


