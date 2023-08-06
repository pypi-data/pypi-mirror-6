from __future__ import print_function

import errno
import logging
import re
import socket
import sys
from pdb import Pdb

PY3 = sys.version_info[0] == 3

def cry(message, stderr=sys.__stderr__):
    logging.critical(message)
    print(message, file=stderr)


class LF2CRLF_FileWrapper(object):
    def __init__(self, fh):
        self.fh = fh
        self.read = fh.read
        self.readline = fh.readline
        self.readlines = fh.readlines
        self.close = fh.close
        self.flush = fh.flush
        self.fileno = fh.fileno

    def __iter__(self):
        return self.fh.__iter__()

    def write(self, data, nl_rex=re.compile("\r?\n")):
        return self.fh.write(nl_rex.sub("\r\n", data))

    def writelines(self, lines, nl_rex=re.compile("\r?\n")):
        return self.fh.writelines(nl_rex.sub("\r\n", line) for line in lines)


class RemotePdb(Pdb):
    """
    This will run pdb as a ephemeral telnet service. Once you connect no one
    else can connect. On construction this object will block execution till a
    client has connected.

    Based on https://github.com/tamentis/rpdb I think ...

    To use this::

        RemotePdb(host='0.0.0.0', port=4444).set_trace()

    Then run: telnet 127.0.0.1 4444
    """
    def __init__(self, host, port, patch_stdstreams=False):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        listen_socket.bind((host, port))
        if not port:
            cry("RemotePdb session open at %s:%s, waiting for connection ..." % listen_socket.getsockname())
            sys.stderr.flush()
        listen_socket.listen(1)
        connection, address = listen_socket.accept()
        cry("RemotePdb accepted connection from %s." % repr(address))
        if PY3:
            self.handle = LF2CRLF_FileWrapper(connection.makefile('rw', buffering=1))
        else:
            self.handle = LF2CRLF_FileWrapper(connection.makefile(bufsize=0))
        Pdb.__init__(self, completekey='tab', stdin=self.handle, stdout=self.handle)
        self.backup = []
        if patch_stdstreams:
            for name in (
                'stderr',
                'stdout',
                '__stderr__',
                '__stdout__',
                'stdin',
                '__stdin__',
            ):
                self.backup.append((name, getattr(sys, name)))
                setattr(sys, name, self.handle)

    def __restore(self):
        cry('Restoring streams: %s ...' % self.backup)
        for name, fh in self.backup:
            setattr(sys, name, fh)
        self.handle.close()

    #def do_continue(self, arg):
    #    self._close_session()
    #    self.set_continue()
    #    return 1
    #do_c = do_cont = do_continue

    def do_quit(self, arg):
        self.__restore()
        self.set_quit()
        return 1
    do_q = do_exit = do_quit

    def set_trace(self, frame=None):
        if frame is None:
            frame = sys._getframe(1).f_back
        try:
            Pdb.set_trace(self, frame)
        except IOError as exc:
            if exc.errno != errno.ECONNRESET:
                raise

    def set_quit(self):
        sys.settrace(None)

def set_trace(host='127.0.0.1', port=0):
    """
    Opens a remote PDB on first available port.
    """
    rdb = RemotePdb(host, port)
    rdb.set_trace()
