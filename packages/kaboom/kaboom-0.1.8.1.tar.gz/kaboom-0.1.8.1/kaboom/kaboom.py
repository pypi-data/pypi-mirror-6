#!/usr/bin/env python
import sys
import argparse

from rethinkdb import RqlDriverError

from app import App


def run():
    parser = argparse.ArgumentParser(description='Command line key-value store.',
                                     add_help=False, )
    parser.add_argument('action', metavar='action', nargs='+', help='action')
    args = parser.parse_args()
    # command = args or 'help'
    if not args.action:
        command = 'help'
    else:
        command = args.action[0]
    try:
        application = App()
    except RqlDriverError as rde:
        sys.exit('''No running rethinkdb instance found\n'''
                 '''Kaboom expects a running rethinkdb instance\n'''
                 '''on localhost at default port''')
    # proc = args.action[0]
    # print 'Command: %s' % proc
    if not hasattr(application, command):
        print "Command `%s` not found" % command
    else:
        sub_commands = args.action[1:] if args.action else None
        if sub_commands:
            application.call(command, *sub_commands)
        else:
            application.call(command)



if __name__ == "__main__":
    run()
