#!/usr/bin/env python
import argparse
from termcolor import colored
from app import App
from constants import ERROR_COLOR, KEY_COLOR, INFO_COLOR
from utils import did_you_mean


def run():
    parser = argparse.ArgumentParser(description='Command line key-value store.',
                                     add_help=False, )
    parser.add_argument('action', metavar='action', nargs='*', help='action')
    args = parser.parse_args()
    # command = args or 'help'
    if not args.action:
        command = 'help'
    else:
        command = args.action[0]
    application = App()

    if not hasattr(application, command):
        print (colored('Command `', ERROR_COLOR) +
               colored(command, INFO_COLOR) +
               colored('`not found, Did you mean `', ERROR_COLOR) +
               colored(did_you_mean(command, App.SUPPORTED_COMMANDS), KEY_COLOR) +
               colored('`', ERROR_COLOR))
    else:
        sub_commands = args.action[1:] if args.action else None
        if sub_commands:
            application.call(command, *sub_commands)
        else:
            application.call(command)


if __name__ == "__main__":
    run()
