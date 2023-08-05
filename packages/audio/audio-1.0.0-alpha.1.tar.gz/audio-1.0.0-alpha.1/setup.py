#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import importlib
from glob import glob
import os
from os.path import splitext
import sys

# Third-Party Libraries
import setuptools

# TODO: externalize "shrink".

metadata = dict(
  name = "audio",
  version = "1.0.0-alpha.1",
  description = "Digital Audio Coding Library",
  author = u"Sébastien Boisgérault",
  author_email = "Sebastien.Boisgerault@mines-paristech.fr",
  license = "MIT License",
)

def build_doc():
    import docgen
    sources = [name for name in glob("*.py") if name != "setup"]
    os.system("python setup.py build")
    for path in glob("build/lib.*"):
        sys.path.insert(0, path)
    output = open("doc.txt", "w")
    doc_header = """\
% Digital Audio Coding -- Library Reference
% S. Boisgérault

"""
    output.write(doc_header)
    for filename in sources:
        source = open(filename).read()
        module = importlib.import_module(splitext(filename)[0])
        output.write(docgen.docgen(module, source))
    output.close()
    os.system("pandoc -s --toc -o doc.pdf doc.txt")
    os.system("pandoc -s --toc -o doc.html doc.txt")

if __name__ == "__main__":
    if "build_doc" in sys.argv[1:]:
        build_doc()
        sys.exit(0)

    py_modules = [splitext(name)[0] for name in glob("*.py") if name != "setup"]
    requirements = "numpy scipy matplotlib sh lsprofcalltree bitstream".split()

    contents = dict(
      py_modules = py_modules,
      scripts = ["shrink"],
      install_requires = requirements,
    )

    kwargs = {}
    kwargs.update(metadata)
    kwargs.update(contents)

    setuptools.setup(**kwargs)

