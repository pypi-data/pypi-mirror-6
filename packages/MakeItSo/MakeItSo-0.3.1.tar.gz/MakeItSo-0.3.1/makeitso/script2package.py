#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
make a package from a .py file
"""

### STUB ###
# TODO:
# - thing to make a setup.py from a .py file
# - use makeitso templates -> directory structure

import optparse
import os
import subprocess
import sys

from .python import PythonModuleTemplate, PythonPackageTemplate

### name transformers.... -> ???

def scriptname2packagename(script):
    return os.path.splitext(os.path.basename(script))[0]



### CLI parsing

def add_options(parser):
    """add options to the OptionParser instance"""
    # TODO: replace with `configuration` package

    parser.add_option('-m', '--module', dest='py_module',
                      action='store_true', default=False,
                      help="create a single-module package with py_modules in setup.py")
    parser.add_option('-n', '--name', dest='name',
                      help="Name of package; default taken from script name")
    parser.add_option('-o', '--output', dest='output',
                      default=os.getcwd(),
                      help="where to output the resulting package [DEFAULT: '.']")

def main(args=sys.argv[1:]):

    # parse command line options
    usage = '%prog [options] script.py'
    class PlainDescriptionFormatter(optparse.IndentedHelpFormatter):
        """description formatter for console script entry point"""
        def format_description(self, description):
            if description:
                return description.strip() + '\n'
            else:
                return ''
    parser = optparse.OptionParser(usage=usage, description=__doc__, formatter=PlainDescriptionFormatter())
    add_options(parser)
    options, args = parser.parse_args(args)
    if len(args) != 1:
        parser.error("Please specify a source script")
    script = args[0]

    # Get package name from script
    if not options.name:
        options.name = scriptname2packagename(script)

    # require a directory (for now)
    if os.path.exists(options.output):
        if not os.path.isdir(options.output):
            parser.error("'%s' is a file" % options.output)
        options.output = os.path.join(options.output, options.name)
        # XXX bad naming
    else:
        raise NotImplementedError("TODO")

    # configure template
    template = PythonModuleTemplate if options.py_module else PythonPackageTemplate
    template = template()

    # get some variables:
    # - author
    # - description
    # - email
    # - repo
    # - url
    variables = {}
    
    # interpolate template
    template.substitute()
    import pdb; pdb.set_trace()
    # TODO

if __name__ == '__main__':
  main()
