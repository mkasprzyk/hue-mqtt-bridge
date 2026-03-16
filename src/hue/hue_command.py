from __future__ import annotations
import json
from enum import Enum
from typing import Optional, Tuple

import attr


class HueCommandType(Enum):
    SWITCH = "switch"
    DIM = "dim"
    COLOR_TEMP = "color_temp"
    COLOR_XY = "color_xy"

    def __str__(self):
        return self.value

    def __repr__(self) -> str:
        return '{}.{}'.format(self.__class__.__name__, self.name)


class SwitchType(Enum):
    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"

    def __str__(self):
        return self.value

    def __repr__(self) -> str:
        return '{}.{}'.format(self.__class__.__name__, self.name)


@attr.frozen
class HueCommand:

    type: HueCommandType
    switch: Optional[SwitchType] = None
    dim: Optional[float] = None
    color_temp: Optional[int] = None  # mirek (e.g. 153-454)
    color_xy: Optional[Tuple[float, float]] = None

    @classmethod
    def create_switch(cls, switch: SwitchType):
        return HueCommand(type=HueCommandType.SWITCH, switch=switch)

    @classmethod
    def create_dim(cls, dim: int):
        if dim == 0:
            return HueCommand(type=HueCommandType.SWITCH, switch=SwitchType.OFF)
        if 1 <= dim <= 100:
            return HueCommand(type=HueCommandType.DIM, dim=float(dim))
        raise ValueError(f"Invalid dim value ({dim})")

    MIREK_MIN, MIREK_MAX = 153, 500  # Hue API typical range

    @classmethod
    def create_color_temp(cls, mirek: int):
        mirek = max(cls.MIREK_MIN, min(cls.MIREK_MAX, int(mirek)))
        return HueCommand(type=HueCommandType.COLOR_TEMP, color_temp=mirek)

    @classmethod
    def create_color_xy(cls, x: float, y: float):
        if not (0 <= x <= 1 and 0 <= y <= 1):
            raise ValueError(f"Invalid xy ({x}, {y}), use 0-1")
        return HueCommand(type=HueCommandType.COLOR_XY, color_xy=(x, y))

    @classmethod
    def parse(cls, text: Optional[str]) -> HueCommand:
        orig_text = text

        if isinstance(text, bytes):
            text = text.decode("utf-8")

        if text:
            text_stripped = text.strip().lstrip("\ufeff")
            if text_stripped.startswith("{"):
                try:
                    obj = json.loads(text_stripped)
                    ct = obj.get("ct") if "ct" in obj else obj.get("CT")
                    if ct is not None:
                        return cls.create_color_temp(int(ct))
                    xy = obj.get("xy") if "xy" in obj else obj.get("XY")
                    if xy is not None and len(xy) >= 2:
                        return cls.create_color_xy(float(xy[0]), float(xy[1]))
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass

            text = text_stripped.upper()

        command = None

        if text:
            if text in ["ON", "TRUE"]:
                command = cls.create_switch(SwitchType.ON)
            elif text in ["OFF", "FALSE"]:
                command = cls.create_switch(SwitchType.OFF)
            elif text == "TOGGLE":
                command = cls.create_switch(SwitchType.TOGGLE)
            else:
                try:
                    value = int(text)
                    if value == 0:
                        return cls.create_switch(SwitchType.OFF)
                    if 1 <= value <= 100:
                        return cls.create_dim(value)
                except ValueError:
                    pass

        if command is None:
            raise ValueError("cannot parse to command ({})!".format(orig_text))

        return command
