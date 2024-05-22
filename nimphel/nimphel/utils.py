#!/usr/bin/env python

from typing import List, Optional, Dict, Any
import re
from enum import Enum, unique

__all__ = ["missing_defaults"]


@unique
class Node(Enum):
    """Type of Node

    Can be used to automatically connect components.
    Can also be used to implement ad-hoc ERC
    """

    IN = 1
    OUT = 2
    INOUT = 3
    VDD = 4
    GND = 5


# Put the Node enums in global space to make using them easier.
# for node in Node:
#     globals()[node.name] = node.value


def missing_defaults(defaults: dict, data: dict) -> List[str]:
    """Check that user values meet default criteria

    Args:
        defaults: Dictionary of default values
        data: User provided data

    Example:
        >>> defaults = {'a': None, 'b': 42}
        >>> provided = {'a': 32}
        >>> missing_defaults(defaults, provided) # []
        >>> provided = {'b': 32}
        >>> missing_defaults(defaults, provided) # ['a']
    """
    required = set(k for k, v in defaults.items() if v is None)
    if not required:
        return []

    provided = set(k for k, v in data.items() if v is not None)
    missing_keys = list(required - provided)
    return missing_keys


class NetGen:
    """Net Generator

    Attributes:
        pattern: Pattern. Defaults to "net{id}"
        start: Start index for the nets. Defaults to 0.
        step: Step between nets. Defaults to 1.

    Example:
        >>> from nimphel.utils import NetGen
        >>> net = NetGen("MyNet-{id}", 1)
        >>> net()  # MyNet-0
        >>> net(2) # MyNet-1
        >>> net()  # MyNet-3
        >>> net = NetGen("net{id:03d}", start=1)
        >>> next(net)  # net001
    """

    def __init__(self, pattern: str = "net{id}", start: int = 0, step: int = 1):
        assert re.match(r".*\{id.*\}.*", pattern)
        self.__pattern: str = pattern
        self.__id: int = start
        self.__step: int = step

    def __call__(self, step: Optional[int] = None):
        """Generates the next net in the series

        TODO: Make it behave like numpy.zeros and create nets in a given shape ?
        """
        self.__id += step or self.__step
        net = self.__pattern.format(id=self.__id)
        return net

    def __iter__(self):
        return self

    def __next__(self):
        return self.__call__()


class Corner(dict):
    """
    See also:
    https://github.com/google/skywater-pdk/blob/main/scripts/python-skywater-pdk/skywater_pdk/corners.py
    """

    CORNER_TYPE_REGEX = re.compile("[tfs]{2}|[TFS]{2}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, k):
        return self[k]

    def __setitem__(self, k, v):
        assert Corner.CORNER_TYPE_REGEX.match(k)
        self[k] = v

    def param(self, k) -> Dict[str, Any]:
        "Get a parameter from all corners"
        return {corner: params.get(k, None) for corner, params in self.items()}


def check_registered(ckt) -> bool:
    """Check that all subcircuits are registered

    Args:
        ckt: The Circuit to check

    Returns:
        True if all subcircuits are registered and False otherwise

    Todo:
        Look for the missing classes and automatically add them
        Maybe return None if correct and a list of names for unregistered circuits.
    """
    inst_names = set([i.name for i in ckt.instances])
    subckt_names = set([i.name for i in ckt.subcircuits])
    return subckt_names.issubset(inst_names)
