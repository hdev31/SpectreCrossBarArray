#!/usr/bin/env python3

from typing import Union, IO, TypeAlias
from abc import ABC, abstractmethod

from nimphel.core import Element, Model, Directive, Instance, Subcircuit, Circuit

"""
Jinja2 Could be used to create template partials for the netlists

```
from jinja2 import Environment, BaseLoader, PackageLoader, select_autoescape
temp = r''
self.template = Environment(loader=BaseLoader).from_string(temp)
self.template.render(**date)
self.template.stream(**data).dump(path)
```
"""

"""
The idea is to provide a general interface similar to the JSON module.

In our case, the encoder/decoded is the Writer, Reader
https://github.com/python/cpython/blob/3.12/Lib/json/encoder.py

"""


class BaseWriter(ABC):
    "Basic Interface for an Element Writer"

    @abstractmethod
    def dump(self, elem: Element, *args, **kwargs) -> Union[str, bytes]:
        return self._write(elem, *args, **kwargs)

    @abstractmethod
    def dump_to_file(self, elem: Element, fp: IO, *args, **kwargs):
        fp.write(self.dump(elem, *args, **kwargs))


class Writer(BaseWriter):
    """Write Elements to different formats."""

    def __default__(self, elem: Element) -> str:
        return str(elem)

    def _write(self, elem: Element, *args, **kwargs) -> Union[str, bytes]:
        fn_name = str(type(elem).__name__).lower()
        try:
            fmt_fn = getattr(self, fn_name)
        except AttributeError:
            fmt_fn = self.__default__
        return fmt_fn(elem, *args, **kwargs)

    def dump(self, elem: Element, *args, **kwargs) -> Union[str, bytes]:
        return super().dump(elem, *args, **kwargs)

    def dump_to_file(self, elem: Element, fp: IO, *args, **kwargs):
        super().dump_to_file(elem, fp, *args, **kwargs)


class SpectreWriter(Writer):
    "Writer for Spectre format"

    def fmt_params(p) -> str:
        return " ".join([f"{k}={v}" if v else str(k) for k, v in p.items()])

    def directive(self, d: Directive, *args, **kwargs) -> str:
        if d.is_raw or not d.args:
            return d.command
        return f"{d.command} {SpectreWriter.fmt_params(d.args)}"

    def model(self, m: Model, *args, **kwargs) -> str:
        return f"model {m.name} {m.base} ({SpectreWriter.fmt_params(m.params)})"

    def instance(self, inst: Instance, *args, **kwargs) -> str:
        nodes = " ".join(str(v) for v in inst.nodes.values())
        uid = inst.uid or 0
        fmt = f"{inst.cap or 'M'}{uid} ({nodes}) {inst.name}"
        if inst.params:
            return f"{fmt} {SpectreWriter.fmt_params(inst.params)}"
        return fmt

    def subcircuit(self, subckt: Subcircuit, *args, **kwargs) -> str:
        nodes = " ".join(str(v) for v in subckt.nodes.keys())
        header = f"subckt {subckt.name} {nodes}\n"
        if subckt.params:
            params = SpectreWriter.fmt_params(subckt.params)
            header = f"{header}parameters {params}\n"
        instances = "\n".join(self.instance(i) for i in subckt.instances)
        return f"{header}{instances}\nends {subckt.name}"

    def circuit(self, ckt: Circuit, *args, **kwargs) -> str:
        instances = "\n".join(map(self._write, ckt.instances))
        subcircuits = "\n".join(map(self._write, ckt.subcircuits))
        directives = "\n".join(map(self._write, ckt.directives))
        lists = [directives, subcircuits, instances]
        return "\n".join([l for l in lists if l])
