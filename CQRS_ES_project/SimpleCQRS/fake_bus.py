from .events import Event
from .commands import Command
from .message import Message
from typing import TypeVar, Generic, Callable, Type, ParamSpec
import abc
from .exceptions import InvalidOperationError
from multipledispatch import dispatch

M = TypeVar('M', bound=Message)
E = TypeVar('E', bound=Event)
C = TypeVar('C', bound=Command)

class ICommandSender(abc.ABC):

    @abc.abstractmethod
    def send(self, command : C) -> None:
        raise NotImplementedError

class IEventPublisher(abc.ABC):

    @abc.abstractmethod
    def publish(self, event : E) -> None:
        raise NotImplementedError

class FakeBus(ICommandSender, IEventPublisher):
    __routes : dict[Type[M], list[Callable[[Message], None]]] = {}

    def register_handler(self, typename : Type[M], handler : Callable[[M], None]) -> None:
        handlers = self.__routes.setdefault(typename, [])

        handlers.append(handler)

    def send(self, command : C) -> None:
        handlers = self.__routes.get(type(command))
        if handlers:
            if len(handlers) != 1:
                raise InvalidOperationError("cannot send to more than one handler")
            handlers[0](command)
        else:
            raise InvalidOperationError("no handler registered")

    def publish(self, event : E) -> None:
        handlers = self.__routes.get(type(event))
        if not handlers:
            return
        for handler in handlers:
            handler(event)
