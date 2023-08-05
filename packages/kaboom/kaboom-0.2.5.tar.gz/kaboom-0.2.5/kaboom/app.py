import os
import sys
import json
from os.path import expanduser
from constants import HELP, STORE_NAME


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

    def __init__(self):
        Store.init_data()
        if Store.data is None:
            _exit('Cannot initialize data')
        # Now we have store taken care of start working

    def call(self, proc, *arguments):
        attr = getattr(self, proc)
        attr(*arguments)
        Store.close()

    def show(self, *args):
        if not args:
            _exit('What to show?')
        # print 'show called with args %s' % args
        if len(args) > 1:
            _exit('Too many arguments')
        name = args[0]
        if name == 'all':
            if len(Store.data):
                print "Showing all items"
                for name, value in Store.data.iteritems():
                    print '%s : %s' % (name, value)
                return
            else:
                print "Nothing to show"
                return
        # print 'show called with %s arguments:%s' % (len(args), args)
        if name in Store.data:
            print Store.data[name]
        else:
            _exit('%s not present' % args[0])

    def add(self, *args):
        if not args:
            print 'adding Nothing'
            return
        # check if same name is present as a command
        name = args[0]
        if len(args) < 2:
            print 'provide value for %s' % name
            return
        value = ' '.join(args[1:])
        # add as a command
        if name not in Store.data:
            Store.data[name] = value
            print "Value %s added for item %s" % (value, name)
        else:
            print "already present, use update(Not supported yet) if you want to change it"

    def delete(self, *args):
        if not args:
            print 'Pass all to delete everything'
            return
        if args[0] == 'all':
            items_to_be_deleted = len(Store.data)
            Store.data = {}
            print 'Deleted everything(%s items)!' % items_to_be_deleted
            return
        name = args[0]

        Store.data.pop(name, None)
        print "Deleted %s" % name

    def update(self, *args):
        if not args:
            print 'update what?'
            return
        if len(args) < 2:
            print "require at least 2 arguments"
            return
        name = args[0]
        value = ' '.join(args[1:])

        if name not in Store.data:
            print "%s not in Store, adding" % name
            self.add(name, value)
            return
        else:
            Store.data[name] = value

    def help(self):
        print HELP





















