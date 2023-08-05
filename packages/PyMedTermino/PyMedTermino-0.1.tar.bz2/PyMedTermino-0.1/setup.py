#! /usr/bin/env python
# -*- coding: utf-8 -*-
# PyMedTermino
# Copyright (C) 2012-2013 Jean-Baptiste LAMY
# LIMICS (Laboratoire d'informatique médicale et d'ingénierie des connaissances en santé), UMR_S 1142
# University Paris 13, Sorbonne paris-Cité, Bobigny, France

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Get SNOMED CT from:
# http://www.nlm.nih.gov/research/umls/licensedcontent/snomedctfiles.html

# Example: SNOMEDCT_DIR = "/home/jiba/telechargements/base_med/SnomedCT_Release_INT_20130731"
SNOMEDCT_DIR = ""

# Get SNOMED CT CORE Problem list from:
# http://www.nlm.nih.gov/research/umls/Snomed/core_subset.html

# Example: SNOMEDCT_CORE_FILE = "/home/jiba/telechargements/base_med/SNOMEDCT_CORE_SUBSET_201308.txt"
SNOMEDCT_CORE_FILE = ""

# Get ICD10 from (NB choose "ClaML" format):
# http://apps.who.int/classifications/apps/icd/ClassificationDownload/DLArea/Download.aspx

# Example: ICD10_DIR = "/home/jiba/telechargements/base_med/icd10"
ICD10_DIR = ""

# Get CIM10 French and German translation from (NB choose "XML" format):
# http://www.icd10.ch/

# Example: CIM10_DIR = "/home/jiba/telechargements/base_med/cim10"
CIM10_DIR = ""






# python setup.py build --snomedct /home/jiba/telechargements/base_med/SnomedCT_Release_INT_20130731 --snomedct-core /home/jiba/telechargements/base_med/SNOMEDCT_CORE_SUBSET_201308.txt --icd10 /home/jiba/telechargements/base_med/icd10 --icd10-translation /home/jiba/telechargements/base_med/cim10

import os, os.path, sys, glob

HERE = os.path.dirname(sys.argv[0]) or "."

i = 0
while i < len(sys.argv):
  if   sys.argv[i] == "--snomedct":          del sys.argv[i]; SNOMEDCT_DIR       = sys.argv[i]; del sys.argv[i]
  elif sys.argv[i] == "--snomedct-core":     del sys.argv[i]; SNOMEDCT_CORE_FILE = sys.argv[i]; del sys.argv[i]
  elif sys.argv[i] == "--icd10":             del sys.argv[i]; ICD10_DIR          = sys.argv[i]; del sys.argv[i]
  elif sys.argv[i] == "--icd10-translation": del sys.argv[i]; CIM10_DIR          = sys.argv[i]; del sys.argv[i]
  else: i += 1


if len(sys.argv) <= 1: sys.argv.append("install")

if ("build" in sys.argv) or (("install" in sys.argv) and (not os.path.exists(os.path.join(HERE, "snomedct.sqlite3")))):
  if SNOMEDCT_DIR:
    cmd = sys.executable + ' %s%sscripts%simport_snomedct.py "%s" "%s"' % (HERE, os.sep, os.sep, SNOMEDCT_DIR, SNOMEDCT_CORE_FILE)
    print(cmd)
    os.system(cmd)
    
if ("build" in sys.argv) or (("install" in sys.argv) and (not os.path.exists(os.path.join(HERE, "icd10.sqlite3")))):
  if ICD10_DIR:
    cmd = sys.executable + ' %s%sscripts%simport_icd10.py "%s" "%s"' % (HERE, os.sep, os.sep, ICD10_DIR, CIM10_DIR)
    print(cmd)
    os.system(cmd)


import distutils.core, distutils.sysconfig

install_dir = distutils.sysconfig.get_python_lib()


distutils.core.setup(
  name         = "PyMedTermino",
  version      = "0.1",
  license      = "LGPLv3+",
  description  = "Medical Terminologies for Python: SNOMED CT, ICD10, UMLS and VCM icons",
  long_description = """PyMedTermino (Medical Terminologies for Python) is a Python module for easy access to the main medical terminologies in Python.
The following terminologies are available: SNOMED CT, ICD10, UMLS, VCM icons (an iconic terminology developped at Paris 13 University).

The main features of PyMedTermino are:
 * A single API for accessing all terminologies
 * Optimized full-text search
 * Access to label, synonyms and translations
 * Manage concepts and relations between concepts
 * Mappings between terminologies, through UMLS or manual mapping files.

SNOMED CT, ICD10 and UMLS data are not included but they can be downloaded for free for academic research. PyMedTermino includes scripts for exporting SNOMED CT and ICD10 data into SQLite3 SQL databases, and can connect to a UMLS server.

PyMedTermino has been created at the LIMICS reseach lab (Laboratoire d'informatique médicale et d'ingénierie des connaissances en santé, UMR_S 1142), University Paris 13, Sorbonne Paris Cité, by Jean-Baptiste Lamy. PyMedTermino is available under the GNU LGPL licence.

Here is an example of what you can do with PyMedTermino:

>>> SNOMEDCT.search("tachycardia*")
[SNOMEDCT[3424008]  # Tachycardia (finding)
, SNOMEDCT[4006006]  # Fetal tachycardia affecting management of mother (disorder)
, SNOMEDCT[6456007]  # Supraventricular tachycardia (disorder)
...]

>>> SNOMEDCT[3424008].parents
[SNOMEDCT[301113001]  # Finding of heart rate (finding)
]

>>> SNOMEDCT[3424008].children
[SNOMEDCT[11092001]  # Sinus tachycardia (finding)
, SNOMEDCT[278086000]  # Baseline tachycardia (finding)
, SNOMEDCT[162992001]  # On examination - pulse rate tachycardia (finding)
...]

>>> list(SNOMEDCT[3424008].ancestors_no_double())
[SNOMEDCT[301113001]  # Finding of heart rate (finding)
, SNOMEDCT[106066004]  # Cardiac rhythm AND/OR rate finding (finding)
, SNOMEDCT[250171008]  # Clinical history and observation findings (finding)
, SNOMEDCT[404684003]  # Clinical finding (finding)
, SNOMEDCT[138875005]  # SNOMED CT Concept (SNOMED RT+CTV3)
...]

>>> SNOMEDCT[3424008].relations
set(['INVERSE_has_definitional_manifestation', 'finding_site', 'interprets', 'has_interpretation', 'INVERSE_associated_with'])

>>> SNOMEDCT[3424008].finding_site
[SNOMEDCT[24964005]  # Cardiac conducting system structure (body structure)
]

>>> SNOMEDCT[3424008] >> VCM   # Maps the SNOMED CT concept to VCM icon
Concepts([
  VCM[u"current--hyper--heart_rhythm"]  # 
])

PyMedTermino can also be used without Python, just for converting SNOMED CT and ICD10 XML data into SQL databases.
""",
  
  author       = "Lamy Jean-Baptiste (Jiba)",
  author_email = "jibalamy@free.fr",
  url          = "http://extranet-limbio.smbh.univ-paris13.fr/html/limbio/claroline/course/index.php?cid=PYMEDTERMINO",
  classifiers  = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Healthcare Industry",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],
  
  package_dir  = {"pymedtermino" : ""},
  packages     = ["pymedtermino", "pymedtermino.utils"],
  package_data = {"pymedtermino" : [file for file in os.listdir(HERE) if file.endswith(".sqlite3")]}
  )


if "clean" in sys.argv:
  try: os.unlink(os.path.join(HERE, "snomedct.sqlite3"))
  except: pass
  try: os.unlink(os.path.join(HERE, "icd10.sqlite3"))
  except: pass

