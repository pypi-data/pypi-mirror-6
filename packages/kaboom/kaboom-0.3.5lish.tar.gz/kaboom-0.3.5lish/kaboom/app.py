import os
import sys
import json
from os.path import expanduser
from termcolor import colored
from constants import HELP, STORE_NAME, ERROR_COLOR, SUCCESS_COLOR, SEPARATOR_COLOR, KEY_COLOR, VALUE_COLOR, INFO_COLOR


home_dir = expanduser('~')


def _exit(message):
    if Store.file_obj:
        Store.file_obj.close()
    sys.exit(message)


class Command(object):

    def __init__(self, name, group=None):
        self.name = name
        self.group = group


class Group(object):

    def __init__(self, name, commands=None):
        self.name = name
        self.commands = commands

    @property
    def count(self):
        return len(self.commands)


class Store(object):

    file_obj = None
    data = None
    _path = os.path.join(home_dir, STORE_NAME)

    @classmethod
    def init_data(cls):
        if os.path.exists(cls._path):
            with open(cls._path, 'r') as file_obj:
                _data = file_obj.read()
                cls.data = json.loads(_data)  # data is loaded
            if cls.data is None:
                _exit('Store load failed with')
        else:
            with open(cls._path, 'w+') as _:  # create the file
                cls.data = {}
                _.write(json.dumps(cls.data))


    @classmethod
    def close(cls):
        cls.save()

    @classmethod
    def save(cls):
        if cls.file_obj:
            cls.close()

        if Store.data is not None:
            with open(cls._path, 'w+') as file_obj:
                file_obj.write(json.dumps(Store.data))


class App(object):

    HELP = 'help'
    SHOW = 'show'
    ADD = 'add'
    DELETE = 'delete'
    UPDATE = 'update'

    SUPPORTED_COMMANDS = (HELP, SHOW, ADD, DELETE, UPDATE)

    def __init__(self):
        Store.init_data()
        if Store.data is None:
            _exit('Cannot initialize data')
        # Now we have store taken care of start working

    def call(self, command, *arguments):
        if command not in self.SUPPORTED_COMMANDS:
            print (colored('Command `', ERROR_COLOR) +
                   colored(command, KEY_COLOR) +
                   colored('` is not supported, "try one of following commands', ERROR_COLOR) +
                   colored('-', SEPARATOR_COLOR) +
                   colored(', '.join(self.SUPPORTED_COMMANDS), INFO_COLOR))
            return
        try:
            attr = getattr(self, command)
        except AttributeError:
            print colored("Command `proc` is not supported, "
                          "try one of following commands %s " % str(self.SUPPORTED_COMMANDS), ERROR_COLOR)
            return
        attr(*arguments)
        Store.close()

    @staticmethod
    def show(*args):
        if not args:
            _exit(colored('What to show?', ERROR_COLOR))
        if len(args) > 1:
            _exit(colored('Too many arguments', ERROR_COLOR))
        name = args[0]
        if name == 'all':
            if len(Store.data):
                print colored("Showing all items", SUCCESS_COLOR)
                for name, value in Store.data.iteritems():
                    print (colored(name, KEY_COLOR) +
                           colored(' : ', SEPARATOR_COLOR) +
                           colored(value, VALUE_COLOR))
                return
            else:
                print colored("Nothing to show", INFO_COLOR)
                return
        if name in Store.data:
            print colored(Store.data[name], VALUE_COLOR)
        else:
            print (colored("`", ERROR_COLOR) +
                   colored(args[0], KEY_COLOR) +
                   colored('` not present', ERROR_COLOR))
            from utils import did_you_mean
            guessed_key = did_you_mean(name, Store.data.keys())
            print (colored("Did you mean", INFO_COLOR) +
                   colored(" : ", SEPARATOR_COLOR) +
                   colored(guessed_key, KEY_COLOR))
            print (colored(guessed_key, KEY_COLOR) +
                   colored(" : ", SEPARATOR_COLOR) +
                   colored(Store.data[guessed_key], VALUE_COLOR))

    @staticmethod
    def add(*args):
        if not args:
            print colored('Adding Nothing', ERROR_COLOR)
            return
        # check if same name is present as a command
        name = args[0]
        if len(args) < 2:
            print (colored('Provide value for `', ERROR_COLOR) +
                   colored(name, KEY_COLOR) +
                   colored('`', ERROR_COLOR))
            return
        value = ' '.join(args[1:])
        # add as a command
        if name not in Store.data:
            Store.data[name] = value
            print (colored("Value ", SUCCESS_COLOR) +
                   colored(value, INFO_COLOR) +
                   colored(" added for item ", SUCCESS_COLOR) +
                   colored(name, KEY_COLOR))
        else:
            print (colored("Already present, use `", ERROR_COLOR) +
                   colored("update", KEY_COLOR) +
                   colored("` if you want to change it", ERROR_COLOR))

    @staticmethod
    def delete(*args):
        if not args:
            print (colored('Pass `', ERROR_COLOR) +
                   colored('all', INFO_COLOR) +
                   colored('` to delete everything', ERROR_COLOR))
            return
        if args[0] == 'all':
            items_to_be_deleted = len(Store.data)
            Store.data = {}
            print colored('Deleted everything(%s items)!' % items_to_be_deleted, SUCCESS_COLOR)
            return
        name = args[0]

        Store.data.pop(name, None)
        print (colored('Deleted `', SUCCESS_COLOR) +
               colored(name, KEY_COLOR) +
               colored('`', SUCCESS_COLOR))

    @staticmethod
    def update(*args):
        if not args:
            print colored('update what?', ERROR_COLOR)
            return
        if len(args) < 2:
            print colored("require at least 2 arguments", ERROR_COLOR)
            return
        name = args[0]
        value = ' '.join(args[1:])

        if name not in Store.data:

            print (colored(name, KEY_COLOR) +
                   colored(" not in Store", ERROR_COLOR))
            from utils import did_you_mean
            guessed_name = did_you_mean(name, Store.data.keys())
            _exit(colored("Did you mean : ", INFO_COLOR) +
                  colored(guessed_name, KEY_COLOR))
            return
        else:
            Store.data[name] = value

    @staticmethod
    def help():
        print colored(HELP, SUCCESS_COLOR)





















