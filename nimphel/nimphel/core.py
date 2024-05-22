#!/usr/bin/env python3

import copy
from pathlib import Path
from dataclasses import dataclass, field, asdict, fields
from collections import defaultdict

from typing import List, Dict, Any, Union, Optional, IO, TypeAlias
from os import PathLike

from nimphel.utils import missing_defaults

#: A Node represents an electrical point in the circuit
Node: TypeAlias = Union[int, str]

#: A map of Node names with default values
NodeMap: TypeAlias = Dict[str, Optional[Node]]

#: A map of Nodes with their respective values
Nodes: TypeAlias = Dict[str, Node]

#: A map of Parameter names with default values
ParamMap: TypeAlias = Dict[str, Optional[Any]]

#: Physical parameters of an Instance
Params: TypeAlias = Dict[str, Any]


@dataclass
class Directive:
    """SPICE Directive

    Attributes:
        command: The actual command the directive executes
        args: Dictionary containing the name and values of the directive arguments

    Example:
        >>> Directive("global", {'0': None, 'gnd!': None})
        >>> d = Directive("this is a raw directive")
        >>> d.is_raw == True
    """

    command: str
    args: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __init__(self, command: str, args: Optional[Dict[str, Any]] = None, **kwargs):
        self.command = command
        self.args = args or {}
        self.args.update(**kwargs)

    def __iter__(self):
        yield from ((field.name, getattr(self, field.name)) for field in fields(self))

    @property
    def is_raw(self) -> bool:
        """Returns true if the directive doesn't have arguments"""
        return not bool(self.args)

    def copy(self):
        return copy.deepcopy(self)

    def __eq__(self, other: object) -> bool:
        """Compare two Directives

        Directives are compared base on the following conditions

        - If both directives are raw, returns True if their command are the same
        - If none of the directives are raw, returns True if their command and args are the same
        - Otherwise, returns False

        Example
            >>> d1 = Directive("tran", {'0':None ,'stop': '100n'})
            >>> d2 = Directive("tran 0 stop=100n")
            >>> d1 == d2 # False
        """
        if not isinstance(other, Directive):
            return False

        if self.is_raw and other.is_raw:
            return self.command == other.command
        if not self.is_raw and not other.is_raw:
            return self.command == other.command and self.args == other.args
        return False


@dataclass
class Model:
    """SPICE Component Model

    Attributes:
        name: The actual name of the model
        base: The base model that this inherits

    Example:
        >>> m = Model('MOD1', 'NPN', {'BF': 50, 'IS': 1e-13, 'VBF': 50})
    """

    name: str
    base: str
    params: Params

    def copy(self):
        return copy.deepcopy(self)

    def __iter__(self):
        yield from ((field.name, getattr(self, field.name)) for field in fields(self))


@dataclass
class Instance:
    """SPICE Instance

    A typical instance is represented as follows in
    M1 (GND VDD) NMOS vth=1.0

    Attributes:
        name: Descriptive name of the instance
        nodes: Dictionary containing the names and values of the Nodes
        params: Dictionary containing the names and values of the Parameters
        uid: Numerical index of the instance
        ctx: Context of the instance.
            If the Instance is generated under the SPICE netlist, it should be `None`, otherwise it should be the name of the subcircuit it was created.
        cap: Letter of the Component used to export in SPICE

    Todo:
        - Allow the ability to add behaviour (e.g. verilogA) to an instance or subcircuit.
    """

    name: str
    nodes: Nodes
    params: Optional[Params] = field(default_factory=dict)
    uid: Optional[int] = None
    ctx: Optional[str] = None
    cap: Optional[str] = None

    def copy(self):
        return copy.deepcopy(self)

    def __iter__(self):
        yield from ((field.name, getattr(self, field.name)) for field in fields(self))


@dataclass
class Component:
    """Component is an Instance Generator

    Each different SPICE component should have their own generator that allows creating as many instances as desired.

    Attributes:
        name: Descriptive name of the Component. All instances generated will share this name.
        nodes: List of Node names or Dictionary containing the names and default values of the Nodes.
        params: Dictionary containing the names and default values of the Component.
        cap: Letter of the Component used to export in SPICE
    """

    name: str
    nodes: NodeMap
    params: Optional[Params] = field(default_factory=dict)
    cap: Optional[str] = None

    def __init__(
        self,
        name: str,
        nodes: Union[NodeMap, List[str]],
        params: Optional[Params] = None,
        cap: Optional[str] = None,
    ):
        self.name: str = name
        if isinstance(nodes, list):
            self.nodes: NodeMap = {n: None for n in nodes}
        else:
            self.nodes = nodes
        self.params: Dict[str, Any] = params or {}
        self.cap: Optional[str] = cap

    def new(
        self,
        nodes: Union[Nodes, List[Node]],
        params: Optional[Params] = None,
        uid: Optional[int] = None,
        ctx: Optional[str] = None,
        *,
        check_defaults: bool = True,
    ) -> Instance:
        """Create a new Instance

        Args:
            nodes: List of Node values or Dicionary containing the names and values of the Nodes
            params: Dictionary containing the names and values of the Parameters.
            uid: The numeric ID of the generated Instance.
            ctx: The context of the generated instance.
            check_defaults: If True, check if the default values of nodes and params are supplied.

        Returns:
            The generated Instance
        """
        if isinstance(nodes, list):
            nodes: Nodes = dict(zip(self.nodes.keys(), nodes))
        params = params if params else {}

        inst_nodes: Nodes = {**self.nodes}
        inst_params: Params = {**self.params}

        if check_defaults:
            missing_nodes = missing_defaults(inst_nodes, nodes)
            if missing_nodes:
                raise ValueError(f"Missing nodes {missing_nodes}")
            inst_nodes.update(**nodes)

            missing_params = missing_defaults(inst_params, params)
            if missing_params:
                raise ValueError(f"Missing parameters {missing_params}")
            inst_params.update(**params)

        return Instance(
            self.name, nodes=nodes, params=params, uid=uid, ctx=ctx, cap=self.cap
        )

    def __call__(self, *args, **kwargs):
        "Alias for `new`"
        return self.new(*args, **kwargs)

    def copy(self):
        return copy.deepcopy(self)

    def __iter__(self):
        yield from [(k, v) for k, v in self.__dict__.items()]

    @classmethod
    def from_instance(
        cls, inst: Instance, reset_nodes: bool = False, reset_params: bool = False
    ) -> "Component":
        """Create a Component from an instance

        Args:
            inst: The Instance object used to create the Component
            reset_nodes: If True the default values of the nodes are set to None
            reset_params: If True the default values of the parameters are set to None

        Returns:
            The Component sharing the same name, nodes and parameters
        """
        nodes: NodeMap = (
            {k: None for k, v in inst.nodes.items()} if reset_nodes else inst.nodes
        )
        params: ParamMap = (
            {k: None for k, v in inst.params.items()} if reset_nodes else inst.params
        )

        return cls(name=inst.name, nodes=nodes, params=inst.params, cap=inst.cap)


@dataclass
class Subcircuit:
    """Subcircuit

    Attributes:
        name: Descriptive name of the subcircuit
        nodes: List of Node names or Dict containing the names and default Node values
        params: Dict containing the name and default parameters
        instance: List of instances inside the subcircuit
        cap: Letter of the Component used to export in SPICE
        uids_map: Dictionary containing the ids of each different Instance
    """

    name: str
    nodes: NodeMap
    params: Optional[Params] = field(default_factory=dict)
    instances: List[Instance] = field(default_factory=list)
    uids_map: Dict[str, int] = field(default_factory=defaultdict(int))
    cap: Optional[str] = None

    def __init__(
        self,
        name: str,
        nodes: Union[NodeMap, List[str]],
        params: Optional[Params] = None,
        cap: Optional[str] = None,
        instances: Optional[List[Instance]] = None,
    ):
        self.name: str = name
        if isinstance(nodes, list):
            self.nodes: NodeMap = {n: None for n in nodes}
        else:
            self.nodes = nodes
        self.params: Params = params or {}
        self.instances: List[Instance] = instances or []
        self.cap: Optional[str] = cap
        self.uids_map: Dict[str, int] = defaultdict(int)

    def add(self, inst: Instance):
        """Add an Instance to the Subcircuit

        A copy of the instance is created and its uid and ctx are modified.

        Args:
            inst: The Instance to add
        """
        inst_copy = inst.copy()
        self.uids_map[inst.name] += 1
        inst_copy.uid = self.uids_map[inst.name]
        inst_copy.ctx = self.name
        self.instances.append(inst_copy)

    def __iadd__(self, other: object):
        assert isinstance(other, Instance)
        self.add(instance)
        return self

    def new(
        self,
        nodes: Union[Nodes, List[Node]],
        params: Optional[Params] = None,
        uid: Optional[int] = None,
        ctx: Optional[str] = None,
        *,
        check_defaults: bool = True,
    ) -> Instance:
        """Create a new Instance

        Args:
            nodes: List of Node values or Dicionary containing the names and values of the Nodes
            params: Dictionary containing the names and values of the Parameters.
            uid: The numeric ID of the generated Instance.
            ctx: The context of the generated instance.
            check_defaults: If True, check if the default values of nodes and params are supplied.

        Returns:
            The generated Instance
        """
        if isinstance(nodes, list):
            nodes: Nodes = dict(zip(self.nodes.keys(), nodes))
        params = params if params else {}

        inst_nodes: Nodes = {**self.nodes}
        inst_params: Params = {**self.params}

        if check_defaults:
            missing_nodes = missing_defaults(inst_nodes, nodes)
            if missing_nodes:
                raise ValueError(f"Missing nodes {missing_nodes}")
            inst_nodes.update(**nodes)

            missing_params = missing_defaults(inst_params, params)
            if missing_params:
                raise ValueError(f"Missing parameters {missing_params}")
            inst_params.update(**params)

        return Instance(self.name, nodes=nodes, params=params, uid=uid, ctx=ctx)

    def copy(self):
        return copy.deepcopy(self)

    def __iter__(self):
        yield from ((field.name, getattr(self, field.name)) for field in fields(self))

    def __contains__(self, o: object):
        return isinstance(o, Instance) and o in self.instances


class Circuit:
    """Circuit a.k.a. SPICE Netlist

    Attributes:
        directives: List of Directives
        subcircuits: List of registered Subcircuits
        instances: List of Instances
        uids_map: Dictionary containing the uids of all different Instances
        path: Optional path to the SPICE netlist
    """

    def __init__(self):
        self.directives: List[Directive] = []
        self.subcircuits: List[Subcircuit] = []
        self.instances: List[Instance] = []
        self.uids_map: Dict[str, int] = defaultdict(int)
        self._path: Optional[PathLike] = None

    def __add_one(self, elem: "Element"):
        """
        If a Subcircuit has been modified after registered, it can't be updated
        TODO: Add a way to update registered elements
        """
        elem_copy = elem.copy()
        if isinstance(elem_copy, Directive):
            self.directives.append(elem_copy)
        if isinstance(elem_copy, Subcircuit):
            if not elem_copy in self.subcircuits:
                self.subcircuits.append(elem_copy)
        if isinstance(elem_copy, Instance):
            self.uids_map[elem_copy.name] += 1
            elem_copy.uid = self.uids_map[elem_copy.name]
            self.instances.append(elem_copy)

    def add(self, args: Union[object, List[object]]):
        if isinstance(args, (list, tuple)):
            for e in args:
                self.__add_one(e)
        else:
            self.__add_one(args.copy())

    def __iadd__(self, args):
        self.add(args)
        return self

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = Path(path).resolve()

    def copy(self):
        return copy.deepcopy(self)

    def __iter__(self):
        yield from [(k, v) for k, v in self.__dict__.items()]

    def __contains__(self, o: object):
        bucket = {
            Directive: self.directives,
            Instance: self.instances,
            Subcircuit: self.directives,
        }
        return o in bucket.get(o.__class__, [])


#: A Physical Element
Element: TypeAlias = Union[Directive, Model, Instance, Subcircuit, Circuit]
