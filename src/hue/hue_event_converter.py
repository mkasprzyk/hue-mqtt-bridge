from typing import Optional, Union

from aiohue.v2 import EventType
from aiohue.v2.models.feature import (
    ColorFeature,
    ColorTemperatureFeature,
    DimmingFeature,
    OnFeature,
)
from aiohue.v2.models.grouped_light import GroupedLight
from aiohue.v2.models.light import Light
from aiohue.v2.models.resource import ResourceTypes
from aiohue.v2.models.room import Room

from src.thing.thing_event import ThingEvent, ThingStatus


class HueEventConverter:

    # noinspection PyShadowingBuiltins
    @classmethod
    def to_thing_event(cls, event_type: EventType, item: Union[Light, GroupedLight, Room], name=None, type=None) -> ThingEvent:
        e = ThingEvent(status=ThingStatus.ERROR)

        e.id = item.id
        e.name = name

        if event_type in [EventType.RESOURCE_DELETED, EventType.DISCONNECTED]:
            e.status = ThingStatus.OFFLINE
            return e

        is_on: Optional[bool] = None

        if hasattr(item, "on") and isinstance(item.on, OnFeature):
            is_on = item.on.on
            e.status = ThingStatus.ON if is_on else ThingStatus.OFF

        if is_on is not None and hasattr(item, "dimming") and isinstance(item.dimming, DimmingFeature):
            e.brightness = item.dimming.brightness if is_on else 0

        if hasattr(item, "color_temperature") and isinstance(item.color_temperature, ColorTemperatureFeature):
            if item.color_temperature.mirek is not None:
                e.color_temp = item.color_temperature.mirek
        if hasattr(item, "color") and isinstance(item.color, ColorFeature) and item.color.xy:
            e.color_xy = (item.color.xy.x, item.color.xy.y)

        if type is not None:
            e.type = type
        else:
            if hasattr(item, "type") and isinstance(item.type, ResourceTypes):
                e.type = str(item.type.value).lower()
                if e.type == "grouped_light":
                    e.type = "group"

        return e
