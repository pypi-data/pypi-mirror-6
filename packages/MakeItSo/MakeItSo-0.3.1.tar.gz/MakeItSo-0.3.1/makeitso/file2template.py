#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
convert a file to a template
"""
# TODO: shell script extension

import argparse
import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
string = (str, unicode)

template = '''#!/usr/bin/env python

"""
template
"""

import argparse
import sys

variables = dict({variables})

template = """{template}"""

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = argparse.ArgumentParser(description=__doc__)
    for variable in variables:
        pass
    options = parser.parse_args(args)

if __name__ == '__main__':
    main()
'''


class File2TemplateParser(argparse.ArgumentParser):
    """argument parser for `%(prog)s`"""

    def __init__(self):
        argparse.ArgumentParser.__init__(self, description=__doc__)
        self.add_argument('input', nargs='?',
                            type=argparse.FileType('r'), default=sys.stdin,
                            help='input file, or read from stdin if ommitted')
        self.add_argument('variables', nargs='*',
                            help="variables to use")
        self.add_argument('-o', '--output', dest='output',
                            type=argparse.FileType('w'), default=sys.stdout,
                            help="output file, or stdout if ommitted'")


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = File2TemplateParser()
    options = parser.parse_args(args)

    # get variable values
    lines = []
    for v in options.variables:
        if '=' in v:
            key, value = v.split('=', 1)
        else:
            key = v
            value = 'None'
        lines.append('{}: {},'.format(repr(key), value))
    varstring = '\n'.join(lines)

    # read the content

    # interpolate the template
    output = template.format(variables=varstring, template='')
    options.output.write(output)

if __name__ == '__main__':
    main()
