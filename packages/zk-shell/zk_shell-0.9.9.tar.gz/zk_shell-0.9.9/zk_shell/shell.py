# -*- coding: utf-8 -*-
#
# a zkCli.sh clone - though not everything is supported currently
# It supports the basic ops:
#
#  python contrib/shell.py localhost:2181
#  (CONNECTED) /> ls
#  zookeeper
#  (CONNECTED) /> create foo 'bar'
#  (CONNECTED) /> get foo
#  bar
#  (CONNECTED) /> cd foo
#  (CONNECTED) /foo> create ish 'barish'
#  (CONNECTED) /foo> cd ..
#  (CONNECTED) /> ls foo
#  ish
#  (CONNECTED) /> create temp- 'temp' true true
#  (CONNECTED) /> ls
#  zookeeper foo temp-0000000001
#  (CONNECTED) /> rmr foo
#  (CONNECTED) />
#  (CONNECTED) /> tree
#  .
#  ├── zookeeper
#  │   ├── config
#  │   ├── quota


from __future__ import print_function

import logging
import os
import re
import shlex
import sys
import time

from kazoo.exceptions import NoNodeError, NotEmptyError

from .acl import ACLReader
from .augumented_client import AugumentedClient
from .augumented_cmd import (
    AugumentedCmd,
    interruptible,
    ensure_params,
    Multi,
    Optional,
    Required,
)
from .copy import copy, CopyError
from .watch_manager import get_watch_manager
from .util import pretty_bytes, to_bool


class Shell(AugumentedCmd):
    def __init__(self, hosts=[], timeout=10):
        AugumentedCmd.__init__(self, ".kz-shell-history")
        self._hosts = hosts
        self._connect_timeout = timeout
        self._zk = None
        self._read_only = False
        self.connected = False

        if len(self._hosts) > 0: self._connect(self._hosts)
        if not self.connected: self.update_curdir("/")

    def connected(f):
        def wrapped(self, args):
          if self.connected:
                return f(self, args)
          print("Not connected.")
        return wrapped

    def check_path_exists(f):
        def wrapped(self, params):
            path = params.path
            params.path = self.abspath(path if path not in ["", "."] else self.curdir)
            if self._zk.exists(params.path):
                return f(self, params)
            print("Path %s doesn't exist" % (path))
            return False
        return wrapped

    def check_path_absent(f):
        def wrapped(self, params):
            path = params.path
            params.path = self.abspath(path if path != '' else self.curdir)
            if not self._zk.exists(params.path):
                return f(self, params)
            print("Path %s already exists" % (path))
        return wrapped

    @connected
    @ensure_params(Required("scheme"), Required("credential"))
    def do_add_auth(self, params):
        self._zk.add_auth(params.scheme, params.credential)

    def help_add_auth(self):
        print("""
allows you to authenticate your session.

example:
  add_auth digest super:s3cr3t
""")

    @connected
    @ensure_params(Required("path"), Multi("acls"))
    @check_path_exists
    def do_set_acls(self, params):
        acls = ACLReader.extract(params.acls)
        try:
            self._zk.set_acls(params.path, acls)
        except Exception as ex:
            print("Failed to set ACLs: %s. Error: %s" % (str(acls), str(ex)))

    def help_set_acls(self):
        print("""
sets ACLs for a given path.

example:
  set_acls /some/path world:anyone:r digest:user:aRxISyaKnTP2+OZ9OmQLkq04bvo=:cdrwa
  set_acls /some/path world:anyone:r username_password:user:p@ass0rd:cdrwa
""")

    @connected
    @ensure_params(Required("path"))
    @check_path_exists
    def do_get_acls(self, params):
        print(self._zk.get_acls(params.path)[0])

    def help_get_acls(self):
        print("""
gets ACLs for a given path.

example:
  get_acls /zookeeper
  [ACL(perms=31, acl_list=['ALL'], id=Id(scheme=u'world', id=u'anyone'))]
""")

    @connected
    @ensure_params(Optional("path"), Optional("watch"))
    @check_path_exists
    def do_ls(self, params):
        kwargs = {"watch": self.watcher} if to_bool(params.watch) else {}
        znodes = self._zk.get_children(params.path, **kwargs)
        print(" ".join(znodes))

    def complete_ls(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    @connected
    @interruptible
    @ensure_params(Required("command"), Required("path"), Optional("debug"), Optional("sleep"))
    @check_path_exists
    def do_watch(self, params):
        wm = get_watch_manager(self._zk)
        if params.command == "start":
            wm.add(params.path, params.debug.lower() == "true")
        elif params.command == "stop":
            wm.remove(params.path)
        elif params.command == "stats":
            repeat = 1
            sleep = 1
            try:
                repeat = int(params.debug)
                sleep = int(params.sleep)
            except ValueError: pass
            if repeat == 0:
                while True:
                    wm.stats(params.path)
                    time.sleep(sleep)
            else:
                for i in xrange(0, repeat):
                    wm.stats(params.path)
                    time.sleep(sleep)
        else:
            print("watch <start|stop> <path> [verbose]")

    def help_watch(self):
        print("""
Recursively watch for all changes under a path.

examples:
  watch start /foo/bar [debug]
  watch stop /foo/bar
  watch stats /foo/bar [repeatN] [sleepN]
""")

    @ensure_params(Required("src"), Required("dst"),
                   Optional("recursive"), Optional("overwrite"), Optional("verbose"))
    def do_cp(self, params):
        try:
            recursive = params.recursive.lower() == "true"
            overwrite = params.overwrite.lower() == "true"
            verbose = params.verbose.lower() == "true"
            copy(params.src, params.dst, recursive, overwrite, verbose)
        except CopyError as ex:
            print(str(ex))

    def help_cp(self):
        print("""
copy from/to local/remote or remote/remote paths.

example:
  cp file://<path> zk://[user:passwd@]host/<path> <recursive> <overwrite> <verbose>
""")

    @connected
    @interruptible
    @ensure_params(Optional("path"), Optional("max_depth"))
    @check_path_exists
    def do_tree(self, params):
        max_depth = 0
        try:
            max_depth = int(params.max_depth) if params.max_depth != "" else 0
        except ValueError: pass

        print(".")
        self._zk.tree(params.path,
                      max_depth,
                      lambda c,l: print(u"%s├── %s" % (u"│   " * l, c)))

    def complete_tree(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_tree(self):
        print("""
print the tree under a given path (optionally only up to a given max depth).

example:
  tree
   .
   ├── zookeeper
   │   ├── config
   │   ├── quota

  tree 1
   .
   ├── zookeeper
   ├── foo
   ├── bar
""")

    @connected
    @ensure_params(Optional("path"))
    @check_path_exists
    def do_du(self, params):
        print(pretty_bytes(self._zk.du(params.path)))

    @connected
    @ensure_params(Optional("path"), Required("match"))
    @check_path_exists
    def do_find(self, params):
        self._zk.find(params.path,
                      params.match,
                      True,
                      0,
                      lambda p: print(p))

    def complete_find(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_find(self):
        print("""
find znodes whose path matches a given text.

example:
  find / foo
  /foo2
  /fooish/wayland
  /fooish/xorg
  /copy/foo
""")

    @connected
    @ensure_params(Required("path"), Required("match"))
    @check_path_exists
    def do_ifind(self, params):
        self._zk.find(params.path,
                      params.match,
                      True,
                      re.IGNORECASE,
                      lambda p: print(p))

    def complete_ifind(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_ifind(self):
        print("""
find znodes whose path matches a given text (regardless of the latter's case).

example:
  ifind / fOO
  /foo2
  /FOOish/wayland
  /fooish/xorg
  /copy/Foo
""")

    @connected
    @ensure_params(Required("path"), Required("content"), Optional("show_matches"))
    @check_path_exists
    def do_grep(self, params):
        show_matches = params.show_matches.lower() == "true"
        self._.zk.grep(params.path,
                       params.content,
                       show_matches,
                       0,
                       lambda p: print(p))

    def complete_grep(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_grep(self):
        print("""
find znodes whose value matches a given text.

example:
  grep / unbound true
  /passwd: unbound:x:992:991:Unbound DNS resolver:/etc/unbound:/sbin/nologin
  /copy/passwd: unbound:x:992:991:Unbound DNS resolver:/etc/unbound:/sbin/nologin
""")

    @connected
    @ensure_params(Required("path"), Required("content"), Optional("show_matches"))
    @check_path_exists
    def do_igrep(self, params):
        show_matches = params.show_matches.lower() == "true"
        self._zk.grep(params.path,
                      params.content,
                      show_matches,
                      re.IGNORECASE,
                      lambda p: print(p))

    def complete_igrep(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_igrep(self):
        print("""
find znodes whose value matches a given text (case-insensite).

example:
  igrep / UNBound true
  /passwd: unbound:x:992:991:Unbound DNS resolver:/etc/unbound:/sbin/nologin
  /copy/passwd: unbound:x:992:991:Unbound DNS resolver:/etc/unbound:/sbin/nologin
""")

    @connected
    @ensure_params(Required("path"))
    @check_path_exists
    def do_cd(self, params):
        self.update_curdir(params.path)

    def complete_cd(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    @connected
    @ensure_params(Required("path"), Optional("watch"))
    @check_path_exists
    def do_get(self, params):
        kwargs = {"watch": self.watcher} if to_bool(params.watch) else {}
        value, stat = self._zk.get(params.path, **kwargs)
        print(value)

    def complete_get(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_get(self):
        print("""
gets the value for a given znode. a watch can be set.

example:
  get /foo
  bar

  # sets a watch
  get /foo true

  # trigger the watch
  set /foo 'notbar'
  WatchedEvent(type='CHANGED', state='CONNECTED', path=u'/foo')
""")

    @connected
    @ensure_params(Required("path"), Optional("watch"))
    @check_path_exists
    def do_exists(self, params):
        kwargs = {"watch": self.watcher} if to_bool(params.watch) else {}
        stat = self._zk.exists(params.path, **kwargs)
        print(stat)

    def complete_exists(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_exists(self):
        print("""
checks if path exists and returns the stat for the znode. a watch can be set.

example:
  exists /foo
  ZnodeStat(czxid=101, mzxid=102, ctime=1382820644375, mtime=1382820693801, version=1, cversion=0, aversion=0, ephemeralOwner=0, dataLength=6, numChildren=0, pzxid=101)

  # sets a watch
  exists /foo true

  # trigger the watch
  rm /foo
  WatchedEvent(type='DELETED', state='CONNECTED', path=u'/foo')
""")

    def watcher(self, watched_event):
        print((str(watched_event)))

    @connected
    @ensure_params(Required("path"),
                   Required("value"),
                   Optional("ephemeral"),
                   Optional("sequence"),
                   Optional("recursive"))
    @check_path_absent
    def do_create(self, params):
        ephemeral = params.ephemeral.lower() == "true"
        sequence = params.sequence.lower() == "true"
        makepath = params.recursive.lower() == "true"
        self._zk.create(params.path,
                        params.value,
                        acl=None,
                        ephemeral=ephemeral,
                        sequence=sequence,
                        makepath=makepath)

    def complete_create(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_create(self):
        print("""
creates a znode in a given path. it can also be ephemeral and/or sequential. it can also be created recursively.

example:
  create /foo 'bar'

  # create an ephemeral znode
  create /foo1 '' true

  # create an ephemeral|sequential znode
  create /foo1 '' true true

  # recursively create a path
  create /very/long/path/here '' false false true

  # check the new subtree
  tree
  .
  ├── zookeeper
  │   ├── config
  │   ├── quota
  ├── very
  │   ├── long
  │   │   ├── path
  │   │   │   ├── here
""")

    @connected
    @ensure_params(Required("path"), Required("value"))
    @check_path_exists
    def do_set(self, params):
        self._zk.set(params.path, params.value)

    def complete_set(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_set(self):
        print("""
sets the value for a znode.

example:
  set /foo 'bar'
""")

    @connected
    @ensure_params(Required("path"))
    @check_path_exists
    def do_rm(self, params):
        try:
            self._zk.delete(params.path)
        except NotEmptyError:
            print("%s is not empty." % (params.path))

    def complete_rm(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    @connected
    @ensure_params(Required("path"))
    @check_path_exists
    def do_rmr(self, params):
        self._zk.delete(params.path, recursive=True)

    @connected
    @ensure_params()
    def do_session_info(self, params):
        print(
"""state=%s
xid=%d
last_zxid=%d
timeout=%d
server=%s""" % (self._zk.state,
                self._zk._connection._xid,
                self._zk.last_zxid,
                self._zk._session_timeout,
                self._zk._connection._socket.getpeername()))

    def help_session_info(self):
        print("""
shows information about the current session (session id, timeout, etc.)

example:
  state=CONNECTED
  xid=4
  last_zxid=11
  timeout=10000
  server=('127.0.0.1', 2181)
""")

    @ensure_params(Optional("host"))
    def do_mntr(self, params):
        host = params.host if params.host != "" else None
        try:
            print(self._zk.mntr(host))
        except AugumentedClient.CmdFailed as ex:
            print(ex)

    @ensure_params(Optional("host"))
    def do_cons(self, params):
        host = params.host if params.host != "" else None
        try:
            print(self._zk.cons(host))
        except AugumentedClient.CmdFailed as ex:
            print(ex)

    @ensure_params(Optional("host"))
    def do_dump(self, params):
        host = params.host if params.host != "" else None
        try:
            print(self._zk.dump(host))
        except AugumentedClient.CmdFailed as ex:
            print(ex)

    def complete_rmr(self, cmd_param_text, full_cmd, start_idx, end_idx):
        return self._complete_path(cmd_param_text, full_cmd)

    def help_rmr(self):
        print("""
recursively deletes a path.

example:
  rmr /foo
""")

    @connected
    @ensure_params(Required("path"))
    @check_path_exists
    def do_sync(self, params):
        self._zk.sync(params.path)

    @ensure_params(Required("hosts"))
    def do_connect(self, params):
        self._connect(params.hosts.split(","))

    def help_connect(self):
        print("""
connects to a host from a list of hosts given.

example:
  connect host1:2181,host2:2181
""")

    @connected
    def do_disconnect(self, args):
        self._disconnect()
        self.update_curdir("/")

    def help_disconnect(self):
        print("""
disconnects from the currently connected host.

example:
  disconnect
""")

    @connected
    def do_pwd(self, args):
        print("%s" % (self.curdir))

    def do_EOF(self, *args):
        self._exit(True)

    def do_quit(self, *args):
        self._exit(False)

    def do_exit(self, *args):
        self._exit(False)

    def _disconnect(self):
        if self._zk: return

        try: self._zk.stop()
        except Exception: pass

    def _connect(self, hosts):
        self._disconnect()
        self._zk = AugumentedClient(",".join(hosts),
                                    read_only=self._read_only)
        try:
            self._zk.start(timeout=self._connect_timeout)
            self.connected = True
        except Exception as ex: print("Failed to connect: %s" % (ex))

        self.update_curdir("/")

    @property
    def state(self):
        return "(%s) " % (self._zk.state if self._zk else "DISCONNECTED")

    def _complete_path(self, cmd_param_text, full_cmd):
        pieces = shlex.split(full_cmd)
        cmd_param = pieces[1] if len(pieces) > 1 else cmd_param_text
        offs = len(cmd_param) - len(cmd_param_text)
        path = cmd_param[:-1] if cmd_param.endswith("/") else cmd_param

        if re.match("^\s*$", path):
            return self._zk.get_children(self.curdir)

        if self._zk.exists(path):
            opts = map(lambda z: "%s/%s" % (path, z),
                       self._zk.get_children(self.abspath(path)))
        elif "/" not in path:
            znodes = self._zk.get_children(self.curdir)
            opts = filter(lambda z: z.startswith(path), znodes)
        else:
            parent = os.path.dirname(path)
            child = os.path.basename(path)
            opts = map(lambda z: "%s/%s" % (parent, z),
                       filter(lambda z: z.startswith(child),
                              self._zk.get_children(parent)))

        return map(lambda x: x[offs:], opts)
