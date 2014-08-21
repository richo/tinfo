#!/usr/bin/env python
# Rich Healey '11 all rights reserved
# Released under GPLv2 or WTFPL at your option
#
# TODO
# - Get yo feature bloat on, colors if we're attached to a TTY
# - port to ruby
# - More attractive visually
# - More intuitive options


import os
import sys
import subprocess
import argparse
import re
from collections import defaultdict
sp = subprocess

class Tmux(object):
    RE = re.compile(r'^(\d+):(\d+): (.*) \((\d+) panes\) \[(\d+)x(\d+)\]')
    KEYS = ('sessno', 'idx', 'title', 'panes', 'sizex', 'sizey')

    def __init__(self, pipe):
        self.sessions = self.build(pipe)

    def build(self, pipe):
        sessions = defaultdict(list)
        for line in pipe:
            line = line.strip()
            dat = Data()
            for key, val in zip(self.KEYS, self.RE.match(line).groups()):
                setattr(dat, key, val)
            sessions[dat.sessno].append(dat)
        return sessions

    def search(self, term):
        to_remove = []
        for idx, clients in self.sessions.iteritems():
            newclients = filter(lambda x: term in x.title, clients)
            if len(newclients) > 0:
                self.sessions[idx] = newclients
            else:
                to_remove.append(idx)
        for i in to_remove:
            del self.sessions[i]

    def pretty_format(self, pipe):
        for idx, clients in self.sessions.iteritems():
            pipe.write("Session %d\n" % (idx))
            for client in clients:
                pipe.write("  %d: %s\n" % (client.idx, client.title))

def _looks_like_size(l):
    if l:
        return l[0] == "[" and l[-1] == "]"
    else:
        return False

class Data(object):
    type_mapping = {
            'sessno': int,
            'winno': int,
            'paneno': int,
            'sizex': int,
            'sizey': int,
            'references': int,
            'idx': int,
            'panes': int,
            'pty': str
        }

    def __setattr__(self, key, value):
        if key in self.type_mapping:
            dict.__setattr__(self, key, self.type_mapping[key](value))
        else:
            dict.__setattr__(self, key, value)

    def iteritems(self):
        return self.__dict__.iteritems()

def get_tmux_info_pipe():
    p = sp.Popen(["tmux", "list-windows", "-a"], bufsize=512,
                      stdin=None, stdout=sp.PIPE, stderr=sp.PIPE, close_fds=True)
    return p.stdout

def in_tmux():
    return "TMUX" in os.environ

def check_args(args):
    if args.attach and not searched(args):
        throw_error("You cannot attach without searching")
    if args.reattach:
        args.attach = True
        args.force = True


def _build_parser():
    #{{{ Argument Parsing
    parser = argparse.ArgumentParser(description="Parse and display tmux info data")
    # Make this the default args I Think
    parser.add_argument('search', metavar='search terms', action='store',
            default=None, nargs='*',
            help="Search for <string> in window names")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help="Enable verbose reporting (show full data)")
    parser.add_argument('-a', '--attach', dest='attach', action='store_true',
            default=False,
            help="Attach to the session, if your search results only return one")
    parser.add_argument('-p', '--pty', dest='searchpty', action='store',
            default=None,
            help="Search for a given {p,t}ty amongst those owned by windows")
    parser.add_argument('-r', '--reattach', dest='reattach', action='store_true',
            default=None,
            help="Reattach to the first session we find that's detached")
    parser.add_argument('-R', '--hard-attach', dest='hardtach', action='store_true',
            default=None,
            help="Do what we've got to do to get a session")
    parser.add_argument('-f', '--force', dest='force', action='store_true',
            default=False,
            help="Force any action which normally refuses")
    parser.add_argument('-G', '--get', dest="get", action='store_true',
            default=False,
            help="Get the target window and bring it here")
    return parser
    #}}}


def main():
    parser = _build_parser()
    args = parser.parse_args()
    check_args(args)
    tmux = Tmux(get_tmux_info_pipe())

    if args.get:
        if not in_tmux() and not args.force:
            throw_error("Can only get sessions from inside tmux")
    if args.search:
        tmux.search(' '.join(args.search))
    if args.get:
        # Assert there's only one session
        keys = tmux.sessions.keys()
        assert len(keys) == 1
        session = tmux.sessions[keys[0]]
        assert len(session) == 1
        client = session[0]
        #i print repr(('tmux', ('tmux', 'move-window', '-s', str(client.idx)+":"+args.search[0])))
        os.execvp('tmux', ('tmux', 'move-window', '-s', '%d:%d' % (keys[0], client.idx)))

    else:
        tmux.pretty_format(sys.stdout)


# FINAL
if __name__ == "__main__":
    try:
        main()
    except NoTmuxError as error:
        throw_error(error.MSG(), error.STATUS())
