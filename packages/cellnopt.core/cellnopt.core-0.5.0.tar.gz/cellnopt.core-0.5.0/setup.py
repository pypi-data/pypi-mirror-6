# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 4309 2014-01-16 14:51:18Z cokelaer $" # for the SVN Id
import sys
import os
from setuptools import setup, find_packages
import glob


#import pip
#def install(package):
#    pip.main(['install', package, '--upgrade'])
try:
    import easydev
    from easydev import get_datafiles
except:
    # install("easydev") does not seem to work well. tried in virtualenv with errors.
    # need to call pip twice... so for now, just copy the relevant code here below
    def get_datafiles(directory="share", match="*"):
        import fnmatch
        datafiles = []
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, match):
                matches.append(os.path.join(root, filename))
                this_filename = os.path.join(root, filename)
                datafiles.append((root, [this_filename]))
        return datafiles




_MAJOR               = 0
_MINOR               = 5
_MICRO               = 0
version              = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
release              = '%d.%d' % (_MAJOR, _MINOR)

metainfo = {
    'authors': {"main": ("Thomas Cokelaer", "cokelaer@ebi.ac.uk")},
    'version': version,
    'license' : 'GPL',
    'download_url' : ['http://pypi.python.org/pypi/cellnopt.core'],
    'url' : ["http://pythonhosted.org/cellnopt.core/"],
    'description': "Functions to manipulate networks and data related to signalling pathways." ,
    'platforms' : ['Linux', 'Unix', 'MacOsX', 'Windows'],
    'keywords' : ['SIF', "MIDAS", "SOP", "Kinexus", "CellNOpt", "CNOGraph"],
    'classifiers' : [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Physics']
    }


namespace = 'cellnopt'

# messy but works for namespaces under Python 2.7
pkgs = [pkg for pkg in find_packages("src")]
top_pkgs = [pkg for pkg in pkgs if  len(pkg.split('.')) < 2]
package_dir = {"": "src"}
for pkg in top_pkgs:
    package_dir[namespace + "." + pkg] = "src" + os.sep + pkg

setup(
    name             = "cellnopt.core",
    version          = version,
    maintainer       = metainfo['authors']['main'][0],
    maintainer_email = metainfo['authors']['main'][1],
    author           = metainfo['authors']['main'][0],
    author_email     = metainfo['authors']['main'][1],
    long_description = open("README.txt").read(),
    keywords         = metainfo['keywords'],
    description      = metainfo['description'],
    license          = metainfo['license'],
    platforms        = metainfo['platforms'],
    url              = metainfo['url'],      
    download_url     = metainfo['download_url'],
    classifiers      = metainfo['classifiers'],

    # package installation
    package_dir = package_dir,
    packages = find_packages("src"),
    namespace_packages = [namespace],

    install_requires = ["easydev>=0.6.5", "networkx", "numpy", "pygraphviz",
        "pandas", "beautifulsoup4", "cellnopt.data"],
    # uncomment if you have share/data files
    data_files = get_datafiles("share", "*"),

    #use_2to3 = True, # causes issue with nosetests
)
