# PyTDMS setup.py
from glob import glob
from os.path import join
import os
#html=glob("cTDMS/html/*")

html=[]
os.chdir("cTDMS")
for root, _, files in os.walk(join("html")):
    for file in files:
        html.append(join(root,  file))


#dlls=glob("*.dll")
#for f in glob("*.lib"):
#    dlls.append(f)
#
#datamodels=[]
#for root, _, files in os.walk(join("DataModels")):
#    for file in files:
#        datamodels.append(join(root,  file))

os.chdir("..")
  
package_data=html+["README", "NI License.rtf",  "setup.py"] 


from distutils.core import setup
setup(
    name = "cTDMS",
    version = "0.91",
    packages=["cTDMS"], 
#    py_modules = ["cTDMS",  "__init__"], 
    package_dir={'cTDMS' : 'cTDMS'},
    package_data={'cTDMS':  package_data},

   
    description = "Reading and writing TDM and TDMS files",
    author = "Alfred Mechsner",
    author_email = "alfred.mechsner@googlemail.com",
   
#    download_url = "",
    keywords = ["TDM", "TDMS" ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        ],
    long_description = """\
Reading and writing TDM and TDMS files

Interface to National Instruments NILIBDDC library using the Python ctypes library.
Version 0.91 for 32bit and 64bit system
"""
)
