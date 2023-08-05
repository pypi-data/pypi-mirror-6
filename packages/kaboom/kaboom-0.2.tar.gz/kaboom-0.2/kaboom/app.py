import sys

try:
    import rethinkdb as r
except ImportError:
    r = None
from constants import DB_NAME, TABLE_NAME, HELP


connection = None


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


class DB(object):

    @classmethod
    def initialize_db(cls):
        r.db_create(DB_NAME).run(connection)
        cls.create_tables()

    @classmethod
    def create_tables(cls):
        r.db(DB_NAME).table_create(TABLE_NAME).run(connection)


class App(object):

    LIST = 'list'
    COMMAND = 'command'

    TYPE = (LIST, COMMAND)

    def __init__(self):
        if not r:
            sys.exit('RethinkDB not found, exiting...')
        global connection
        connection = r.connect('localhost', 28015)
        self.connection = connection
        if not connection:
            print "database is not available"
            return
        self.bootstrap()

    def bootstrap(self):
        """
        simple list,
        each element has
        1. command name  - index command here
        2. type - command or list

        """
        if DB_NAME in r.db_list().run(self.connection):
            # print "Database already initialized"
            return
        DB.initialize_db()

    def call(self, proc, *arguments):
        attr = getattr(self, proc)
        attr(*arguments)

    def show(self, *args):
        if not args:
            sys.exit('What to show?')
        # print 'show called with args %s' % args
        if len(args) > 1:
            sys.exit('Too many arguments')
        name = args[0]
        if name == 'all':
            items = r.db(DB_NAME).table(TABLE_NAME).run(connection)
            print "Showing all items"
            for item in items:
                print '%s : %s' % (item['name'], item['value'])
            sys.exit()
        # print 'show called with %s arguments:%s' % (len(args), args)
        if r.db(DB_NAME).table(TABLE_NAME).filter(r.row["name"] == name).count().run(connection):
            item = r.db(DB_NAME).table(TABLE_NAME).filter(r.row["name"] == args[0]).run(connection)
            print [_ for _ in item][0]['value']
        else:
            sys.exit('%s not present' % args[0])
        #TODO now we know element is in database fetch it and show

    def add(self, *args):
        if not args:
            sys.exit('adding Nothing')
        # check if same name is present as a command
        name = args[0]
        if len(args) < 2:
            sys.exit('provide value for %s' % name)
        value = ' '.join(args[1:])
        # add as a command
        if not r.db(DB_NAME).table(TABLE_NAME).filter(r.row["name"] == args[0]).count().run(connection):
            r.db(DB_NAME).table(TABLE_NAME).insert({
                'name': name,
                'value': value
            }).run(connection)

            print "Value %s added for item %s" % (value, name)
        else:
            print "already present in database, use update if you want to change it"

    def delete(self, *args):
        if not args:
            sys.exit('Pass all to delete everything')
        if args[0] == 'all':
            items_to_be_deleted = r.db(DB_NAME).table(TABLE_NAME).count().run(connection)
            r.db(DB_NAME).table(TABLE_NAME).delete().run(connection)
            sys.exit('Deleted everything(%s items)!' % items_to_be_deleted)
        name = args[0]

        r.db(DB_NAME).table(TABLE_NAME).filter(r.row["name"] == name).delete().run(connection)
        print "Deleted %s" % name

    def help(self):
        print HELP





















