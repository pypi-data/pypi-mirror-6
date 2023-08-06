"""ZeroMQ RPC"""

import asyncio
import os
import random
import struct
import time
import sys

import zmq


from collections import ChainMap
from functools import partial

from aiozmq.log import logger

from .base import (
    GenericError,
    NotFoundError,
    ParametersError,
    Service,
    _BaseProtocol,
    _BaseServerProtocol,
    )
from .util import (
    _MethodCall,
    _fill_error_table,
    )


__all__ = [
    'connect_rpc',
    'serve_rpc',
    ]


@asyncio.coroutine
def connect_rpc(*, connect=None, bind=None, loop=None,
                error_table=None, translation_table=None, timeout=None):
    """A coroutine that creates and connects/binds RPC client.

    Return value is a client instance.
    """
    # TODO: describe params
    # TODO: add a way to pass exception translator
    # TODO: add a way to pass value translator
    if loop is None:
        loop = asyncio.get_event_loop()

    transp, proto = yield from loop.create_zmq_connection(
        lambda: _ClientProtocol(loop, error_table=error_table,
                                translation_table=translation_table),
        zmq.DEALER, connect=connect, bind=bind)
    return RPCClient(loop, proto, timeout=timeout)


@asyncio.coroutine
def serve_rpc(handler, *, connect=None, bind=None, loop=None,
              translation_table=None):
    """A coroutine that creates and connects/binds RPC server instance."""
    # TODO: describe params
    # TODO: add a way to pass value translator
    if loop is None:
        loop = asyncio.get_event_loop()

    transp, proto = yield from loop.create_zmq_connection(
        lambda: _ServerProtocol(loop, handler,
                                translation_table=translation_table),
        zmq.ROUTER, connect=connect, bind=bind)
    return Service(loop, proto)


_default_error_table = _fill_error_table()


class _ClientProtocol(_BaseProtocol):
    """Client protocol implementation."""

    REQ_PREFIX = struct.Struct('=HH')
    REQ_SUFFIX = struct.Struct('=Ld')
    RESP = struct.Struct('=HHLd?')

    def __init__(self, loop, *, error_table=None, translation_table=None):
        super().__init__(loop, translation_table=translation_table)
        self.calls = {}
        self.prefix = self.REQ_PREFIX.pack(os.getpid() % 0x10000,
                                           random.randrange(0x10000))
        self.counter = 0
        if error_table is None:
            self.error_table = _default_error_table
        else:
            self.error_table = ChainMap(error_table, _default_error_table)

    def msg_received(self, data):
        try:
            header, banswer = data
            pid, rnd, req_id, timestamp, is_error = self.RESP.unpack(header)
            answer = self.packer.unpackb(banswer)
        except Exception:
            logger.critical("Cannot unpack %r", data, exc_info=sys.exc_info())
            return
        call = self.calls.pop(req_id, None)
        if call is None:
            logger.critical("Unknown answer id: %d (%d %d %f %d) -> %s",
                            req_id, pid, rnd, timestamp, is_error, answer)
        elif call.cancelled():
            logger.info("The future for %d has been cancelled, "
                        "skip the received result.", req_id)
        else:
            if is_error:
                call.set_exception(self._translate_error(*answer))
            else:
                call.set_result(answer)

    def _translate_error(self, exc_type, exc_args):
        found = self.error_table.get(exc_type)
        if found is None:
            return GenericError(exc_type, tuple(exc_args))
        else:
            return found(*exc_args)

    def _new_id(self):
        self.counter += 1
        if self.counter > 0xffffffff:
            self.counter = 0
        return (self.prefix + self.REQ_SUFFIX.pack(self.counter, time.time()),
                self.counter)

    def call(self, name, args, kwargs):
        bname = name.encode('utf-8')
        bargs = self.packer.packb(args)
        bkwargs = self.packer.packb(kwargs)
        header, req_id = self._new_id()
        assert req_id not in self.calls, (req_id, self.calls)
        fut = asyncio.Future(loop=self.loop)
        self.calls[req_id] = fut
        self.transport.write([header, bname, bargs, bkwargs])
        return fut


class RPCClient(Service):

    def __init__(self, loop, proto, *, timeout):
        super().__init__(loop, proto)
        self._timeout = timeout

    @property
    def call(self):
        """Return object for dynamic RPC calls.

        The usage is:
        ret = yield from client.call.ns.func(1, 2)
        """
        return _MethodCall(self._proto, timeout=self._timeout)

    def with_timeout(self, timeout):
        """Return a new RPCClient instance with overriden timeout"""
        return self.__class__(self._loop, self._proto, timeout=timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        return


class _ServerProtocol(_BaseServerProtocol):

    REQ = struct.Struct('=HHLd')
    RESP_PREFIX = struct.Struct('=HH')
    RESP_SUFFIX = struct.Struct('=Ld?')

    def __init__(self, loop, handler, *, translation_table=None):
        super().__init__(loop, handler, translation_table=translation_table)
        self.prefix = self.RESP_PREFIX.pack(os.getpid() % 0x10000,
                                            random.randrange(0x10000))

    def msg_received(self, data):
        try:
            peer, header, bname, bargs, bkwargs = data
            pid, rnd, req_id, timestamp = self.REQ.unpack(header)

            args = self.packer.unpackb(bargs)
            kwargs = self.packer.unpackb(bkwargs)
        except Exception as exc:
            logger.critical("Cannot unpack %r", data, exc_info=sys.exc_info())
            return
        try:
            func = self.dispatch(bname.decode('utf-8'))
            args, kwargs, ret_ann = self._check_func_arguments(
                func, args, kwargs)
        except (NotFoundError, ParametersError) as exc:
            fut = asyncio.Future(loop=self.loop)
            fut.add_done_callback(partial(self.process_call_result,
                                          req_id=req_id, peer=peer))
            fut.set_exception(exc)
        else:
            if asyncio.iscoroutinefunction(func):
                fut = asyncio.async(func(*args, **kwargs), loop=self.loop)
                fut.add_done_callback(partial(self.process_call_result,
                                              req_id=req_id, peer=peer,
                                              return_annotation=ret_ann))
            else:
                fut = asyncio.Future(loop=self.loop)
                fut.add_done_callback(partial(self.process_call_result,
                                              req_id=req_id, peer=peer,
                                              return_annotation=ret_ann))
                try:
                    fut.set_result(func(*args, **kwargs))
                except Exception as exc:
                    fut.set_exception(exc)

    def process_call_result(self, fut, *, req_id, peer,
                            return_annotation=None):
        try:
            ret = fut.result()
            # TODO: allow `ret` to be validated against None
            if return_annotation is not None:
                ret = return_annotation(ret)
            prefix = self.prefix + self.RESP_SUFFIX.pack(req_id,
                                                         time.time(), False)
            self.transport.write([peer, prefix, self.packer.packb(ret)])
        except Exception as exc:
            prefix = self.prefix + self.RESP_SUFFIX.pack(req_id,
                                                         time.time(), True)
            exc_type = exc.__class__
            exc_info = (exc_type.__module__ + '.' + exc_type.__name__,
                        exc.args)
            self.transport.write([peer, prefix, self.packer.packb(exc_info)])
