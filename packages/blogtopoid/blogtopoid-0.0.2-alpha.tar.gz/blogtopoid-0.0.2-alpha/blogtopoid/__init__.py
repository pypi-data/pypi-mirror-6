"""
blogtopoid
"""
from __future__ import unicode_literals
from __future__ import print_function

import pkg_resources
from argparse import ArgumentParser


#hashstore = Hashstore('hashstore.json')

def main():
    """ run blogtopoid.

    '--quickstart': set up a new (empty) blog
    '--post': generate new blog post
    given no arguments blogtopoid renders all posts and pages.
    """
    from . import commands
    dist = pkg_resources.get_distribution("blogtopoid")

    parser = ArgumentParser(description="simple blog generator")
    parser.add_argument('--version', action='version', version='%(prog)s ' +
                                                               dist.version)
    parser.add_argument('--quickstart', help="create empty blog skeleton",
                        action="store_true")
    parser.add_argument('--post', help="create new post", action="store_true")
    args = parser.parse_args()

    if args.quickstart:
        commands.quickstart()

    elif args.post:
        commands.new_post()

    else:
        commands.generate()
