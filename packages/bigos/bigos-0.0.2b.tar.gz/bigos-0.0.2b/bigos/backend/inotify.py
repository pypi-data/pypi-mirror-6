#/bin/env python2
# encoding: utf8

import os
from contextlib import closing
from ctypes import *

libc = cdll.LoadLibrary('libc.so.6')

class Flags:
    ACCESS = 0x00000001 # File was accessed. 
    MODIFY = 0x00000002 # File was modified. 
    ATTRIB = 0x00000004 # Metadata changed. 
    CLOSE_WRITE = 0x00000008 # Writtable file was closed. 
    CLOSE_NOWRITE = 0x00000010 # Unwrittable file closed. 
    CLOSE = (CLOSE_WRITE | CLOSE_NOWRITE) # Close. 
    OPEN = 0x00000020 # File was opened. 
    MOVED_FROM = 0x00000040 # File was moved from X. 
    MOVED_TO = 0x00000080 # File was moved to Y. 
    MOVE = (MOVED_FROM | MOVED_TO) # Moves. 
    CREATE = 0x00000100 # Subfile was created. 
    DELETE = 0x00000200 # Subfile was deleted. 
    DELETE_SELF = 0x00000400 # Self was deleted. 
    MOVE_SELF = 0x00000800 # Self was moved. 

    ONLYDIR = 0x01000000 # Only watch the path if it is
    ISDIR = 0x40000000 # Event occurred against dir.  

    ALL_EVENTS =     (ACCESS | MODIFY | ATTRIB | CLOSE_WRITE  \
                              | CLOSE_NOWRITE | OPEN | MOVED_FROM         \
                              | MOVED_TO | CREATE | DELETE                \
                              | DELETE_SELF | MOVE_SELF)

    def __init__(self, val):
        self.val = val

    def __contains__(self, v):
        """
        >>> Flags.OPEN in Flags(0x00000020)
        True
        >>> Flags.DELETE in Flags(0x00000020)
        False
        """
        return self.val & v == v

    def __iter__(self):
        """
        >>> list(Flags(Flags.CREATE | Flags.ISDIR))
        ['CREATE', 'ISDIR']
        """
        for k, v in self.__class__.__dict__.iteritems():
            if k != k.upper():
                continue

            if v in self:
                yield k

    def __repr__(self):
        return ' | '.join(iter(self))

class InotifyEvent(Structure):
    '''
    struct inotify_event {
        int      wd;       /* Watch descriptor */
        uint32_t mask;     /* Mask of events */
        uint32_t cookie;   /* Unique cookie associating related
                              events (for rename(2)) */
        uint32_t len;      /* Size of name field */
        char     name[];   /* Optional null-terminated name */
    };
    '''
    _fields_ = [
        ('wd', c_int),
        ('mask', c_uint32),
        ('cookie', c_uint32),
        ('len', c_uint32),
        ('name', c_char * 2048),
    ]

    @property
    def flags(self):
        return Flags(self.mask)

    @property
    def is_dir(self):
        return bool(self.mask & Flags.ISDIR)

    @property
    def type(self):
        if self.mask & Flags.MODIFY or self.mask & Flags.CLOSE_WRITE:
            return 'modified'
        elif self.mask & Flags.CREATE:
            return 'created'
        elif self.mask & Flags.DELETE:
            return 'removed'
        if self.mask & Flags.ACCESS or self.mask & Flags.CLOSE_NOWRITE:
            return 'read'
        else:
            return 'other'


class Inotify:
    def __init__(self):
        self.fd = libc.inotify_init()
        self.wd_to_dir = {}
        self.dir_to_wd = {}

    def add_watch(self, filename, flags=Flags.ALL_EVENTS):
        r = libc.inotify_add_watch(
            self.fd, c_char_p(filename), c_uint32(flags))
        if r <= 0: raise IOError('inotify_add_watch returned %d', r)

        return r

    def add_dir_watch(self, path):
        wd = self.add_watch(path)
        self.wd_to_dir[wd] = path
        self.dir_to_wd[path] = wd

    def remove_dir_watch(self, path):
        wd = self.dir_to_wd[path]
        r = libc.inotify_rm_watch(self.fd, wd)
        if r != 0: raise IOError('inotify_rm_watch returned %d', r)
        # TODO
        #del self.dir_to_wd[path]
        #del self.wd_to_dir[wd]

    def get_event(self):
        event_buf = InotifyEvent()
        r = libc.read(self.fd, byref(event_buf), sizeof(event_buf))
        if r <= 0: raise IOError('read returned %d', r)

        event_buf.path = os.path.join(
            self.wd_to_dir[event_buf.wd], event_buf.name)

        return event_buf

    def close(self):
        libc.close(self.fd)


def generate_events(dir_path):
    i = Inotify()
    for root, dirs, files in os.walk(dir_path):
        i.add_dir_watch(root)

    with closing(i):
        while True:
            ev = i.get_event()
            flags = ev.flags

            # TODO: handle directory moves correctly
            if Flags.ISDIR in flags:
                if Flags.CREATE in flags or Flags.MOVED_TO in flags:
                    #print '** add dir', ev.path
                    i.add_dir_watch(ev.path)
                if Flags.MOVED_FROM in flags:
                    pass
                    #print '** rm dir', ev.path
                    #i.remove_dir_watch(ev.path)

            yield [ev]
