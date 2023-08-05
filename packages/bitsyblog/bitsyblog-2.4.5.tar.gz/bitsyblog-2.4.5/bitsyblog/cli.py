#!/usr/bin/env python

"""
command line interface to bitsyblog
"""

import optparse
import sys
from user import FilespaceUsers

def main(args=sys.argv[1:]):
    """command line entry point for user creation"""

    # command line parser
    usage = '%prog [options] directory user'
    parser = optparse.OptionParser(usage=usage)
    options, args = parser.parse_args(args)

    # get user name
    if len(args) != 2:
        parser.error("directory, user not specified")
    directory, name = args

    # create user
    users = FilespaceUsers(directory)

if __name__ == '__main__':
    main()
