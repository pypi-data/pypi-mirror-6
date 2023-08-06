import select
import socket
import ssl
import errno
from math import ceil

from simpy.io.base import (BaseIOEnvironment, BaseTCPSocket, BaseSSLSocket,
        socket_error)


class Environment(BaseIOEnvironment):
    def __init__(self, fds=None, type='epoll'):
        BaseIOEnvironment.__init__(self, fds)

        if type == 'epoll':
            self._read_flag = select.EPOLLIN
            self._write_flag = select.EPOLLOUT
            self._poll = select.epoll()
            self._iowait = self._epoll_iowait
        elif type == 'poll':
            self._read_flag = select.POLLIN
            self._write_flag = select.POLLOUT
            self._poll = select.poll()
            self._iowait = self._poll_iowait
        else:
            raise RuntimeError('Invalid poll type "%s"' % type)

    def _epoll_iowait(self, timeout):
        # TODO Expect timeout to be an int of milliseconds? 
        if timeout is not None:
            timeout = ceil(timeout * 1000) / 1000
        else:
            timeout = -1

        for fd, eventmask in self._poll.poll(timeout):
            sock = self.fds[fd]
            sock._flags = 0
            self._poll.modify(fd, 0)

            if eventmask & self._read_flag:
                sock._ready_read()

            if eventmask & self._write_flag:
                sock._ready_write()

    def _poll_iowait(self, timeout):
        # TODO Expect timeout to be an int of milliseconds? 
        if timeout is not None:
            timeout = ceil(timeout * 1000)

        for fd, eventmask in self._poll.poll(timeout):
            sock = self.fds[fd]
            sock._flags = 0
            self._poll.modify(fd, 0)

            if eventmask & self._read_flag:
                sock._ready_read()

            if eventmask & self._write_flag:
                sock._ready_write()


class TCPSocket(BaseTCPSocket):
    def __init__(self, env, sock=None):
        BaseTCPSocket.__init__(self, env, sock)

        self._read_flag = env._read_flag
        self._write_flag = env._write_flag

        self._flags = 0
        self.env._poll.register(self.fileno(), self._flags)

    def _do_read(self):
        try:
            self._reader._value = self.sock.recv(self._reader.amount)
            if not self._reader._value:
                self._reader.ok = False
                self._reader._value = socket_error(errno.ECONNRESET)
            else:
                self._reader.ok = True
            self.env.schedule(self._reader)
        except BlockingIOError:
            self._flags |= self._read_flag
            self.env._poll.modify(self.fileno(), self._flags)
            return
        except socket.error as e:
            self._reader.fail(e)
        self._reader = None

    def _do_write(self):
        try:
            self._writer._value = self.sock.send(self._writer.data)
            self._writer.ok = True
            self.env.schedule(self._writer)
        except BlockingIOError:
            self._flags |= self._write_flag
            self.env._poll.modify(self.fileno(), self._flags)
            return
        except socket.error as e:
            self._writer.fail(e)
        self._writer = None

    def _do_accept(self):
        try:
            self._reader._value = type(self)(self.env, self.sock.accept()[0])
            self._reader.ok = True
            self.env.schedule(self._reader)
        except BlockingIOError:
            self._flags |= self._read_flag
            self.env._poll.modify(self.fileno(), self._flags)
            return
        except socket.error as e:
            self._reader.fail(e)
        self._reader = None

    def close(self):
        # TODO Figure out if this behaviour is really usefull. Might require
        # the addition of methods that check for the sockets state.
        if self.sock.fileno() >= 0:
            del self.env.fds[self.sock.fileno()]
            self.env._poll.unregister(self.fileno())

            # Fail reader and writer events.
            if self._reader is not None:
                self._reader.fail(socket_error(errno.EBADF))
                self._reader = None
            if self._writer is not None:
                self._writer.fail(socket_error(errno.EBADF))
                self._writer = None
        self.sock.close()


class SSLSocket(BaseSSLSocket):
    def __init__(self, env, sock=None, **kwargs):
        BaseSSLSocket.__init__(self, env, sock, **kwargs)

        self._read_flag = env._read_flag
        self._write_flag = env._write_flag

        self._flags = 0
        self.env._poll.register(self.fileno(), self._flags)

    def _do_read(self):
        try:
            self._reader._value = self.sock.recv(self._reader.amount)
            if not self._reader._value:
                self._reader.ok = False
                self._reader._value = socket_error(errno.ECONNRESET)
            else:
                self._reader.ok = True
            self.env.schedule(self._reader)
        except (BlockingIOError, ssl.SSLWantReadError):
            self._flags |= self._read_flag
            self.env._poll.modify(self.fileno(), self._flags)
            return
        except socket.error as e:
            self._reader.fail(e)
        self._reader = None

    def _do_write(self):
        try:
            self._writer._value = self.sock.send(self._writer.data)
            self._writer.ok = True
            self.env.schedule(self._writer)
        except (BlockingIOError, ssl.SSLWantWriteError):
            self._flags |= self._write_flag
            self.env._poll.modify(self.fileno(), self._flags)
            return
        except socket.error as e:
            self._writer.fail(e)
        self._writer = None

    def _do_accept(self):
        try:
            sock = type(self)(self.env, self.sock.accept()[0])
            sock.handshake(False)
            self._reader._value = sock
            self._reader.ok = True
            self.env.schedule(self._reader)
        except BlockingIOError:
            self._flags |= self._read_flag
            self.env._poll.modify(self.fileno(), self._flags)
            return
        except socket.error as e:
            self._reader.fail(e)
        self._reader = None

    def _ssl_handshake_read(self):
        self._flags |= self._read_flag
        self.env._poll.modify(self.fileno(), self._flags)
        self._ssl_event = self.env.event()

    def _ssl_handshake_write(self):
        self._flags |= self._write_flag
        self.env._poll.modify(self.fileno(), self._flags)
        self._ssl_event = self.env.event()

    def close(self):
        if self.sock.fileno() >= 0:
            del self.env.fds[self.sock.fileno()]
            self.env._poll.unregister(self.fileno())
            # FIXME Abort ssl_events of the handshake.

            # Fail events.
            if self._reader is not None:
                self._reader.fail(socket_error(errno.EBADF))
                self._reader = None
            if self._writer is not None:
                self._writer.fail(socket_error(errno.EBADF))
                self._writer = None
        self.sock.close()
