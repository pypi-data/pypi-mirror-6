#/bin/env python2
# encoding: utf8

import platform

if platform.system() == 'Linux':
    from .inotify import generate_events
else:
    from .polling import generate_events
