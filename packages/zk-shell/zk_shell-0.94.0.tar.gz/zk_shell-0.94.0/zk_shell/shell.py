# -*- coding: utf-8 -*-

"""
zkCli.sh clone.
It supports the basic ops plus a few handy extensions:
 (CONNECTED) /> ls
 zookeeper
 (CONNECTED) /> create foo 'bar'
 (CONNECTED) /> get foo
 bar
 (CONNECTED) /> cd foo
 (CONNECTED) /foo> create ish 'barish'
 (CONNECTED) /foo> cd ..
 (CONNECTED) /> ls foo
 ish
 (CONNECTED) /> create temp- 'temp' true true
 (CONNECTED) /> ls
 zookeeper foo temp-0000000001
 (CONNECTED) /> rmr foo
 (CONNECTED) />
 (CONNECTED) /> tree
 .
 ├── zookeeper
 │   ├── config
 │   ├── quota
"""

from __future__ import print_function

from functools import wraps
import os
import re
import shlex
import signal
import sys
import time
import zlib

from kazoo.exceptions import (
    BadVersionError,
    InvalidACLError,
    NoAuthError,
    NodeExistsError,
    NoNodeError,
    NotEmptyError,
    ZookeeperError,
)
from kazoo.protocol.states import KazooState
from kazoo.security import OPEN_ACL_UNSAFE, READ_ACL_UNSAFE

from .acl import ACLReader
from .augumented_client import AugumentedClient
from .augumented_cmd import (
    AugumentedCmd,
    BooleanOptional,
    IntegerOptional,
    interruptible,
    ensure_params,
    Multi,
    Optional,
    Required,
)
from .copy import CopyError, Proxy
from .watch_manager import get_watch_manager
from .util import pretty_bytes, to_bool


def connected(func):
    """ check connected, fails otherwise """
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        if not self.connected:
            print("Not connected.", file=self.output)
        else:
            try:
                return func(*args, **kwargs)
            except NoAuthError:
                print("Not authenticated.", file=self.output)
    return wrapper


def check_path_exists(func):
    """ check paths exists """
    @wraps(func)
    def wrapper(*args):
        self = args[0]
        params = args[1]
        path = params.path
        params.path = self.resolve_path(path)
        if self.client.exists(params.path):
            return func(self, params)
        print("Path %s doesn't exist" % (path), file=self.output)
        return False
    return wrapper


def check_path_absent(func):
    """ check path doesn't exist """
    @wraps(func)
    def wrapper(*args):
        self = args[0]
        params = args[1]
        path = params.path
        params.path = self.resolve_path(path)
        if not self.client.exists(params.path):
            return func(self, params)
        print("Path %s already exists" % (path))
    return wrapper


def default_watcher(watched_event):
    print(str(watched_event))


# pylint: disable=R0904
class Shell(AugumentedCmd):
    """ main class """
    def __init__(self, hosts=None, timeout=10, output=sys.stdout, setup_readline=True, async=True):
        AugumentedCmd.__init__(self, ".kz-shell-history", setup_readline)
        self._hosts = hosts if hosts else []
        self._connect_timeout = timeout
        self._output = output
        self._zk = None
        self._read_only = False
        self._async = async
        self.connected = False

        if len(self._hosts) > 0:
            self._connect(self._hosts)
        if not self.connected:
            self.update_curdir("/")

    def _complete_path(self, cmd_param_text, full_cmd, *_):
        """ completes paths """
        pieces = shlex.split(full_cmd)
        cmd_param = pieces[1] if len(pieces) > 1 else cmd_param_text
        offs = len(cmd_param) - len(cmd_param_text)
        path = cmd_param[:-1] if cmd_param.endswith("/") else cmd_param

        if re.match(r"^\s*$", path):
            return self._zk.get_children(self.curdir)

        if self._zk.exists(path):
            children = self._zk.get_children(self.resolve_path(path))
            opts = ["%s/%s" % (path, znode) for znode in children]
        elif "/" not in path:
            znodes = self._zk.get_children(self.curdir)
            opts = [znode for znode in znodes if znode.startswith(path)]
        else:
            parent = os.path.dirname(path)
            child = os.path.basename(path)
            matching = [znode for znode in self._zk.get_children(parent) if znode.startswith(child)]
            opts = ["%s/%s" % (parent, znode) for znode in matching]

        return [opt[offs:] for opt in opts]

    @property
    def client(self):
        """ the connected ZK client, if any """
        return self._zk

    @property
    def output(self):
        """ the io output object """
        return self._output

    @connected
    @ensure_params(Required("scheme"), Required("credential"))
    def do_add_auth(self, params):
        """
        allows you to authenticate your session.
        example:
        add_auth digest super:s3cr3t
        """
        self._zk.add_auth(params.scheme, params.credential)

    @connected
    @ensure_params(Required("path"), Multi("acls"))
    @check_path_exists
    def do_set_acls(self, params):
        """
        sets ACLs for a given path.
        example:
        set_acls /some/path world:anyone:r digest:user:aRxISyaKnTP2+OZ9OmQLkq04bvo=:cdrwa
        set_acls /some/path world:anyone:r username_password:user:p@ass0rd:cdrwa
        """
        try:
            acls = ACLReader.extract(params.acls)
        except ACLReader.BadACL as ex:
            print("Failed to set ACLs: %s." % (ex), file=self._output)
            return

        try:
            self._zk.set_acls(params.path, acls)
        except (NoNodeError, BadVersionError, InvalidACLError, ZookeeperError) as ex:
            print("Failed to set ACLs: %s. Error: %s" % (str(acls), str(ex)), file=self._output)

    complete_set_acls = _complete_path

    @connected
    @interruptible
    @ensure_params(Required("path"), IntegerOptional("depth", -1), BooleanOptional("ephemerals"))
    @check_path_exists
    def do_get_acls(self, params):
        """
        gets ACLs for a given path.

        get_acls <path> [depth] [ephemerals]

        by the default this won't recurse. 0 means infinite recursion.

        examples:
        get_acls /zookeeper
        [ACL(perms=31, acl_list=['ALL'], id=Id(scheme=u'world', id=u'anyone'))]

        get_acls /zookeeper -1
        /zookeeper: [ACL(perms=31, acl_list=['ALL'], id=Id(scheme=u'world', id=u'anyone'))]
        /zookeeper/config: [ACL(perms=31, acl_list=['ALL'], id=Id(scheme=u'world', id=u'anyone'))]
        /zookeeper/quota: [ACL(perms=31, acl_list=['ALL'], id=Id(scheme=u'world', id=u'anyone'))]
        """
        def replace(plist, oldv, newv):
            try:
                plist.remove(oldv)
                plist.insert(0, newv)
            except ValueError:
                pass

        for path, acls in self._zk.get_acls_recursive(params.path, params.depth, params.ephemerals):
            replace(acls, READ_ACL_UNSAFE[0], "WORLD_READ")
            replace(acls, OPEN_ACL_UNSAFE[0], "WORLD_ALL")
            print("%s: %s" % (path, acls), file=self._output)

    complete_get_acls = _complete_path

    @connected
    @ensure_params(Optional("path"), Optional("watch"))
    @check_path_exists
    def do_ls(self, params):
        kwargs = {"watch": default_watcher} if to_bool(params.watch) else {}
        znodes = self._zk.get_children(params.path, **kwargs)
        print(" ".join(znodes), file=self._output)

    complete_ls = _complete_path

    @connected
    @interruptible
    @ensure_params(Required("command"), Required("path"), Optional("debug"), Optional("sleep"))
    @check_path_exists
    def do_watch(self, params):
        """
        Recursively watch for all changes under a path.
        examples:
        watch start /foo/bar [debug]
        watch stop /foo/bar
        watch stats /foo/bar [repeatN] [sleepN]
        """
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
            except ValueError:
                pass
            if repeat == 0:
                while True:
                    wm.stats(params.path)
                    time.sleep(sleep)
            else:
                for _ in range(0, repeat):
                    wm.stats(params.path)
                    time.sleep(sleep)
        else:
            print("watch <start|stop> <path> [verbose]")

    @ensure_params(Required("src"), Required("dst"),
                   BooleanOptional("recursive"), BooleanOptional("overwrite"),
                   BooleanOptional("async"), BooleanOptional("verbose"),
                   IntegerOptional("max_items", 0))
    def do_cp(self, params):
        """
        copy from/to local/remote or remote/remote paths.

        src and dst can be any of:

        /some/path (in the connected server)
        file://<path>
        zk://[user:passwd@]host/<path>
        json://!some!path!backup.json/some/path

        with a few restrictions. bare in mind the semantic differences
        that znodes have with filesystem directories - so recursive copying
        from znodes to an fs could lose data, but to a JSON file it would
        work just fine.

        examples:
        cp /some/znode /backup/copy-znode  # local
        cp file://<path> zk://[user:passwd@]host/<path> <recursive> <overwrite> <async> <verbose> <max_items>
        cp /some/path json://!home!user!backup.json/ true true
        """

        # default to zk://connected_host, if connected
        src_connected_zk = dst_connected_zk = False
        if self.connected:
            zk_url = self._zk.zk_url()

            # if these are local paths, make them absolute paths
            if not re.match(r"^\w+://", params.src):
                params.src = "%s%s" % (zk_url, self.resolve_path(params.src))
                src_connected_zk = True

            if not re.match(r"^\w+://", params.dst):
                params.dst = "%s%s" % (zk_url, self.resolve_path(params.dst))
                dst_connected_zk = True

        try:
            src = Proxy.from_string(params.src, True, params.async, params.verbose)
            if src_connected_zk:
                src.need_client = False
                src.client = self._zk

            dst = Proxy.from_string(params.dst,
                                    exists=None if params.overwrite else False,
                                    async=params.async,
                                    verbose=params.verbose)
            if dst_connected_zk:
                dst.need_client = False
                dst.client = self._zk

            src.copy(dst, params.recursive, params.max_items)
        except CopyError as ex:
            print(str(ex), file=self._output)

    complete_cp = _complete_path

    @connected
    @interruptible
    @ensure_params(Optional("path"), IntegerOptional("max_depth"))
    @check_path_exists
    def do_tree(self, params):
        """
        print the tree under a given path (optionally only up to a given max depth).
        examples:
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
        """
        print(".", file=self._output)
        for child, level in self._zk.tree(params.path, params.max_depth):
            print(u"%s├── %s" % (u"│   " * level, child), file=self._output)

    complete_tree = _complete_path

    @connected
    @ensure_params(Optional("path"))
    @check_path_exists
    def do_du(self, params):
        print(pretty_bytes(self._zk.du(params.path)), file=self._output)

    @connected
    @ensure_params(Optional("path"), Required("match"))
    @check_path_exists
    def do_find(self, params):
        """
        find znodes whose path matches a given text.
        example:
        find / foo
        /foo2
        /fooish/wayland
        /fooish/xorg
        /copy/foo
        """
        for path in self._zk.find(params.path, params.match, 0):
            print(path, file=self._output)

    complete_find = _complete_path

    @connected
    @ensure_params(Required("path"), Required("match"))
    @check_path_exists
    def do_ifind(self, params):
        """
        find znodes whose path matches a given text (regardless of the latter's case).
        example:
        ifind / fOO
        /foo2
        /FOOish/wayland
        /fooish/xorg
        /copy/Foo
        """
        for path in self._zk.find(params.path, params.match, re.IGNORECASE):
            print(path, file=self._output)

    complete_ifind = _complete_path

    @connected
    @ensure_params(Required("path"), Required("content"), BooleanOptional("show_matches"))
    @check_path_exists
    def do_grep(self, params):
        """
        find znodes whose value matches a given text.
        example:
        grep / unbound true
        /passwd: unbound:x:992:991:Unbound DNS resolver:/etc/unbound:/sbin/nologin
        /copy/passwd: unbound:x:992:991:Unbound DNS resolver:/etc/unbound:/sbin/nologin
        """
        self.grep(params.path, params.content, 0, params.show_matches)

    complete_grep = _complete_path

    @connected
    @ensure_params(Required("path"), Required("content"), BooleanOptional("show_matches"))
    @check_path_exists
    def do_igrep(self, params):
        """
        find znodes whose value matches a given text (case-insensite).
        example:
        igrep / UNBound true
        /passwd: unbound:x:992:991:Unbound DNS resolver:/etc/unbound:/sbin/nologin
        /copy/passwd: unbound:x:992:991:Unbound DNS resolver:/etc/unbound:/sbin/nologin
        """
        self.grep(params.path, params.content, re.IGNORECASE, params.show_matches)

    complete_igrep = _complete_path

    def grep(self, path, content, flags, show_matches):
        for path, matches in self._zk.grep(path, content, flags):
            if show_matches:
                print("%s:" % (path), file=self._output)
                for match in matches:
                    print(match, file=self._output)
            else:
                print(path, file=self._output)

    @connected
    @ensure_params(Required("path"))
    @check_path_exists
    def do_cd(self, params):
        self.update_curdir(params.path)

    complete_cd = _complete_path

    @connected
    @ensure_params(Required("path"), Optional("watch"))
    @check_path_exists
    def do_get(self, params):
        """
        gets the value for a given znode. a watch can be set.

        example:
        get /foo
        bar

        # sets a watch
        get /foo true

        # trigger the watch
        set /foo 'notbar'
        WatchedEvent(type='CHANGED', state='CONNECTED', path=u'/foo')
        """
        kwargs = {"watch": default_watcher} if to_bool(params.watch) else {}
        value, _ = self._zk.get(params.path, **kwargs)

        # maybe it's compressed?
        try:
            value = zlib.decompress(value)
        except (zlib.error, TypeError):
            pass

        print(value, file=self._output)

    complete_get = _complete_path

    @connected
    @ensure_params(Required("path"), Optional("watch"))
    def do_exists(self, params):
        """
        checks if path exists and returns the stat for the znode. a watch can be set.

        example:
        exists /foo
        ZnodeStat(czxid=101, mzxid=102, ctime=1382820644375, mtime=1382820693801, version=1, cversion=0, aversion=0, ephemeralOwner=0, dataLength=6, numChildren=0, pzxid=101)

        # sets a watch
        exists /foo true

        # trigger the watch
        rm /foo
        WatchedEvent(type='DELETED', state='CONNECTED', path=u'/foo')
        """
        kwargs = {"watch": default_watcher} if to_bool(params.watch) else {}
        path = self.resolve_path(params.path)
        stat = self._zk.exists(path, **kwargs)
        if stat:
            print(stat, file=self._output)
        else:
            print("Path %s doesn't exist" % (params.path), file=self._output)

    complete_exists = _complete_path

    @connected
    @ensure_params(Required("path"),
                   Required("value"),
                   BooleanOptional("ephemeral"),
                   BooleanOptional("sequence"),
                   BooleanOptional("recursive"))
    @check_path_absent
    def do_create(self, params):
        """
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
        """
        try:
            self._zk.create(params.path,
                            params.value,
                            acl=None,
                            ephemeral=params.ephemeral,
                            sequence=params.sequence,
                            makepath=params.recursive)
        except NodeExistsError:
            print("Path %s exists" % (params.path), file=self._output)

    complete_create = _complete_path

    @connected
    @ensure_params(Required("path"), Required("value"))
    @check_path_exists
    def do_set(self, params):
        """
        sets the value for a znode.

        example:
        set /foo 'bar'
        """
        self._zk.set(params.path, params.value)

    complete_set = _complete_path

    @connected
    @ensure_params(Required("path"))
    @check_path_exists
    def do_rm(self, params):
        try:
            self._zk.delete(params.path)
        except NotEmptyError:
            print("%s is not empty." % (params.path))

    complete_rm = _complete_path

    @connected
    @ensure_params()
    def do_session_info(self, params):
        """
        shows information about the current session (session id, timeout, etc.)

        example:
        state=CONNECTED
        xid=4
        last_zxid=11
        timeout=10000
        server=('127.0.0.1', 2181)
        """
        print(
"""state=%s
xid=%d
last_zxid=%d
timeout=%d
server=%s""" % (self._zk.state,
                self._zk.xid,
                self._zk.last_zxid,
                self._zk.session_timeout,
                self._zk.server), file=self._output)

    @ensure_params(Optional("host"))
    def do_mntr(self, params):
        host = params.host if params.host != "" else None
        try:
            print(self._zk.mntr(host), file=self._output)
        except AugumentedClient.CmdFailed as ex:
            print(ex)

    @ensure_params(Optional("host"))
    def do_cons(self, params):
        host = params.host if params.host != "" else None
        try:
            print(self._zk.cons(host), file=self._output)
        except AugumentedClient.CmdFailed as ex:
            print(ex)

    @ensure_params(Optional("host"))
    def do_dump(self, params):
        host = params.host if params.host != "" else None
        try:
            print(self._zk.dump(host), file=self._output)
        except AugumentedClient.CmdFailed as ex:
            print(ex)

    @connected
    @ensure_params(Required("path"))
    @check_path_exists
    def do_rmr(self, params):
        """
        recursively deletes a path.

        example:
        rmr /foo
        """
        self._zk.delete(params.path, recursive=True)

    complete_rmr = _complete_path

    @connected
    @ensure_params(Required("path"))
    @check_path_exists
    def do_sync(self, params):
        self._zk.sync(params.path)

    @ensure_params(Required("hosts"))
    def do_connect(self, params):
        """
        connects to a host from a list of hosts given.

        example:
        connect host1:2181,host2:2181
        """

        # TODO: we should offer autocomplete based on prev hosts.
        self._connect(params.hosts.split(","))

    @connected
    def do_disconnect(self, args):
        """
        disconnects from the currently connected host.
        """
        self._disconnect()
        self.update_curdir("/")

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
        if self._zk:
            self._zk.stop()
            self._zk = None
        self.connected = False

    def _connect(self, hosts):
        self._disconnect()
        self._zk = AugumentedClient(",".join(hosts), read_only=self._read_only)
        if self._async:
            self._connect_async()
        else:
            self._connect_sync()

    def _connect_async(self):
        def listener(state):
            if state == KazooState.CONNECTED:
                self.connected = True
                self.update_curdir("/")
                # hack to restart sys.stdin.readline()
                print("", file=self.output)
                os.kill(os.getpid(), signal.SIGUSR2)
        self._zk.add_listener(listener)
        self._zk.start_async()#timeout=self._connect_timeout)
        self.update_curdir("/")

    def _connect_sync(self):
        try:
            self._zk.start(timeout=self._connect_timeout)
            self.connected = True
        except self._zk.handler.timeout_exception as ex:
            print("Failed to connect: %s" % (ex), file=self._output)
        self.update_curdir("/")

    @property
    def state(self):
        return "(%s) " % (self._zk.state if self._zk else "DISCONNECTED")
