import abc
import asyncio
import inspect

from aiozmq import interface

from .packer import _Packer


class Error(Exception):
    """Base RPC exception"""


class GenericError(Error):
    """Error used for all untranslated exceptions from rpc method calls."""

    def __init__(self, exc_type, args):
        super().__init__(exc_type, args)
        self.exc_type = exc_type
        self.arguments = args


class NotFoundError(Error, LookupError):
    """Error raised by server if RPC namespace/method lookup failed."""


class ParametersError(Error, ValueError):
    """Error raised by server when RPC method's parameters could not
    be validated against their annotations."""


class ServiceClosedError(Exception):
    """RPC Service has been closed."""


class AbstractHandler(metaclass=abc.ABCMeta):
    """Abstract class for server-side RPC handlers."""

    __slots__ = ()

    @abc.abstractmethod
    def __getitem__(self, key):
        raise KeyError

    @classmethod
    def __subclasshook__(cls, C):
        if cls is AbstractHandler:
            if any("__getitem__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


class AttrHandler(AbstractHandler):
    """Base class for RPC handlers via attribute lookup."""

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError


def method(func):
    """Marks a decorated function as RPC endpoint handler.

    The func object may provide arguments and/or return annotations.
    If so annotations should be callable objects and
    they will be used to validate received arguments and/or return value.
    """
    func.__rpc__ = {}
    func.__signature__ = sig = inspect.signature(func)
    for name, param in sig.parameters.items():
        ann = param.annotation
        if ann is not param.empty and not callable(ann):
            raise ValueError("Expected {!r} annotation to be callable"
                             .format(name))
    ann = sig.return_annotation
    if ann is not sig.empty and not callable(ann):
        raise ValueError("Expected return annotation to be callable")
    return func


class Service(asyncio.AbstractServer):
    """RPC service.

    Instances of Service (or
    descendants) are returned by coroutines that creates clients or
    servers.

    Implementation of AbstractServer.
    """

    def __init__(self, loop, proto):
        self._loop = loop
        self._proto = proto

    @property
    def transport(self):
        """Return the transport.

        You can use the transport to dynamically bind/unbind,
        connect/disconnect etc.
        """
        transport = self._proto.transport
        if transport is None:
            raise ServiceClosedError()
        return transport

    def close(self):
        if self._proto.transport is None:
            return
        self._proto.transport.close()

    @asyncio.coroutine
    def wait_closed(self):
        if self._proto.transport is None:
            return
        waiter = asyncio.Future(loop=self._loop)
        self._proto.done_waiters.append(waiter)
        yield from waiter


class _BaseProtocol(interface.ZmqProtocol):

    def __init__(self, loop, translation_table=None):
        self.loop = loop
        self.transport = None
        self.done_waiters = []
        self.packer = _Packer(translation_table=translation_table)

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport = None
        for waiter in self.done_waiters:
            waiter.set_result(None)
