#/bin/env python2
# encoding: utf8

from . import main, on

@on(r'^[^/]*/([^.][^/]*\/)*[^.][^/]*$')
def file_task(ev):
    print 'file event:', ev.path, ev.type
    if hasattr(ev, 'flags'):
        print 'inotify flags:', ev.flags

main('.')
