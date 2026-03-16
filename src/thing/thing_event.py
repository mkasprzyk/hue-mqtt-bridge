from enum import Enum
from typing import Optional, Dict, Tuple

import attr

from src.utils.time_utils import TimeUtils


class ThingStatus(Enum):
    ERROR = "error"
    OFF = "off"
    OFFLINE = "offline"
    ON = "on"


@attr.define
class ThingEvent:

    status: Optional[ThingStatus] = None
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None

    brightness: Optional[float] = None
    color_temp: Optional[int] = None   # mirek
    color_xy: Optional[Tuple[float, float]] = None

    def to_data(self) -> Dict[str, any]:
        data = {
            "name": self.name
        }

        if not self.status:
            data["status"] = "error"
        else:
            data["status"] = self.status.value

        if self.brightness is not None:
            data["brightness"] = int(round(self.brightness))
        if self.color_temp is not None:
            data["color_temp"] = self.color_temp
        if self.color_xy is not None:
            data["color_xy"] = [round(self.color_xy[0], 4), round(self.color_xy[1], 4)]

        data["timestamp"] = TimeUtils.now(no_ms=True)

        return data
