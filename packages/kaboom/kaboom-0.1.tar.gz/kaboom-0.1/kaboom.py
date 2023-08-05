#/usr/bin/python

from app import App
import argparse


parser = argparse.ArgumentParser(description='Kaboom arguments.')
parser.add_argument('strings', metavar='proc', type=str, nargs='+',
                    help='processes')

args = parser.parse_args()
# print args.accumulate(args.strings)

allowed_proce = ['add', 'remove', 'show']


def run():
    application = App()
    proc = args.strings[0]
    # print 'Command: %s' % proc
    if not hasattr(application, proc):
        print "Command `%s` not found" % proc
    else:
        application.call(proc, *tuple(args.strings[1:]))


if __name__ == "__main__":
    run()
