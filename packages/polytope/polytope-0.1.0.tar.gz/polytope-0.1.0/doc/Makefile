# Makefile for Sphinx and Epydoc-generated documentation
#
#
# NOTES: - By default, the "--graph=classtree" option is used when invoking
#          Epydoc, causing class inheritance to be shown in an image.  This
#          option requires the Graphviz (http://www.graphviz.org/) program dot
#          to be installed.

PKG_REL     = ../polytope

# Epydoc options
EPYDOC        = epydoc
EPYBUILDDIR   = api_doc
EPYOPTS       = --graph=classtree --no-sourcecode

# Sphinx options
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

.PHONY: api

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  api        to make API documentation using Epydoc"
	@echo "  clean      delete build output"

clean:
	-rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) . $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

api:
	mkdir -p $(BUILDDIR)/$(EPYBUILDDIR)
	$(EPYDOC) $(EPYOPTS) --html -v --name=Polytope --url=https://github.com/tulip-control/polytope -o $(BUILDDIR)/$(EPYBUILDDIR) $(PKG_REL)/{__init__.py,esp.py,plot.py,polytope.py,prop2partition.py,quickhull.py}
