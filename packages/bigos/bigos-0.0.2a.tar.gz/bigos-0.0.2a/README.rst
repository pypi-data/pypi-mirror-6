Bigos - do stuff on file change

Use the ``on`` decorator to run tasks when matching files are modified:

::

    from bigos import on, main

    @on(r'^[^/]*/([^.][^/]*\/)*[^.][^/]*$')
    def non_dotfile_task(ev):
        print 'file event:', ev.path

    if __name__ == '__main__':
        main('.')

Use the backend to get the raw event stream:

::

    from bigos.backend import generate_events

    for event_list in generate_events():
        print event_list

Installation
============

::

    pip install bigos

Supported platforms
===================

-  On modern Linux kernels bigos will use a ctypes inotify wrapper
-  Other systems are supported via a filesystem polling backend

License
=======

Copyright (C) 2014 Paweł Stiasny

Bigos is released under the GNU General Public License, see COPYING for
details.
