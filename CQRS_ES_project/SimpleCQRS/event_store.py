import abc
from .guid import Guid
from typing import Sequence
from .events import Event
from .fake_bus import IEventPublisher
from .exceptions import ConcurrencyError

class IEventStore(abc.ABC):
    @abc.abstractmethod
    def save_events(self, aggregate_id : Guid, events : Sequence[Event], expected_version : int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_events_for_aggregate(self, aggregate_id : Guid) -> list[Event]:
        raise NotImplementedError

class EventDescriptor:
    def __init__(self, id : Guid, event_data : Event, version : int) -> None:
        self.__event_data = event_data
        self.__version = version
        self.__id = id

    @property
    def event_data(self) -> Event:
        return self.__event_data

    @property
    def version(self) -> int:
        return self.__version

    @property
    def id(self) -> Guid:
        return self.__id

class EventStore(IEventStore):

    def __init__(self, publisher :IEventPublisher) -> None:
        self.__publisher = publisher

    __current : dict[Guid, list[EventDescriptor]] = {}

    def save_events(self, aggregate_id: Guid, events: Sequence[Event], expected_version: int) -> None:
        event_descriptors = self.__current.get(aggregate_id)
        if not event_descriptors:
            event_descriptors = []
            self.__current[aggregate_id] = event_descriptors

        elif event_descriptors[len(event_descriptors)-1].version != expected_version and expected_version != -1:
            raise ConcurrencyError()

        i = expected_version

        for event in events:
            i += 1
            event.version = i
            event_descriptors.append(EventDescriptor(aggregate_id, event, i))
            self.__publisher.publish(event)

    def get_events_for_aggregate(self, aggregate_id: Guid) -> list[Event] | None:
        event_descriptors = self.__current.get(aggregate_id)
        if event_descriptors is None:
            return None

        return [desc.event_data for desc in event_descriptors]
