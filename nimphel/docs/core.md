This section will show the different. It is important to state that since this framework is still in development, some mechanisms and classes could change in the future.

!!! note
    Although this framework is simulator agnostic, the next examples will be focused for the Spectre simulator.

## SPICE Directives

Directives refer to raw SPICE statements normally used to control the simulator.

Directives are created through the `Directive` class and can be created in 2 ways:

- A single string containing the raw directive
- The directive command and a dictionary containing the arguments of the directive. Usually, directives are formatted as `name param1=value param2=value ...`, but can vary depending on the simulator used.

When supplying a dictionary with the parameters of the directive, the value `None` can be used to indicate that a parameter should only use the key instead of the key value pair. The following examples show the different ways of definining directives.

```python title="Creating directives"
from nimphel.core import Directive

# Raw string directive
Directive("simulator lang=spectre")

# Directive with parameters
Directive("simulator", {"lang": "spectre"})

# The info parameter is None
Directive(
    "modelParameter",
    {"info": None, "what": "models", "where": "rawfile"}
    )
# modelParameter info what=models where=rawfile
```

It is important to keep in mind that directives are always created as the name and the dictionary of parameters when reading a circuit from a netlist file.

## Instances

Instances are one the the core constituents of SPICE and therefore of this framework. As the name implies, they refer to specific instances of electronic components inside a SPICE netlist. The way instances are described depends on the SPICE specificiation used, but they usually follow this structure.

```text title="Instance in SPICE format"
M1 (GND VDD) NMOS vth=1.0
```

In NIMPHEL, the previous instance would be created in the following manner:

```python title="Creating a simple instance"
from nimphel.core import Instance

Instance(
    name="NMOS", nodes=dict(GND=0, VDD=1),
    params={"vth": 1.0}, cxt=None,
    cap="M", uid=1
)
```

- The `name` refers to the electronic name of the component, in this case an NMOS transistor.

- The `nodes` attributes is used to identify the electrical conections of the component. It's a dictionary containg the name of each node and it's respective value. For this example, the node names are _GND_ and _VDD_ while the values are 0 and 1. Note than Instance nodes **cannot** be empty or be None.

- The `params` dictionary contains the instance parameters of the component.

- The `ctx` keyword allows defining the context under which an instance is created. If an instance is created at the top level (e.g. directly in the circuit) it defaults to `None`. However, when an instance is created as part of a subcircuit, the context is the name of the subcircuit. This allows us to create sort of a dependency graph of each of the components and subcircuits.

- The `cap` keyword allows defining the string used to identify the component type in the SPICE netlist. More information about this can be seen in the [exporting](writers.md)

- The `uid` refers to the numeric ID of the Instance in the SPICE netlist.


Instances can also be copied and modified once they have been created.

```python title="Copying and updating an instance"
from nimphel.core import Instance

nmos = Instance(
    name="NMOS", nodes={'D': 1, 'G': 2, 'S': 3 'B': 'GND'},
    params={"vth": 1.0}, cxt=None,
    cap="M", uid=1
    )

pmos = nmos.copy()
pmos.name = "PMOS"
pmos.params["vth"] = -1.0
```

However, creating instances in this way can become cumbersome very quickly, specially if we are instanciating the same electronic component multiple times. The following section shows how to create components to allow creating multiple instances of the same component in a simple and reusable manner.

## Components

Components in NIMPHEL can be seen as _instance generators_ for a desired electronic component. To create instances of the same type of component, a `Component` object needs to be created, that will be later used to create new instances. 

A `Component` can be created in the following manner:

```python title="Creating a component"
from nimphel.core import Component

# Only the Node names are supplied
R = Component("R", ['P', 'N'])

# The Node names and the default value for "R" is provided
R = Component("R", ['P', 'N'], {'R': 1e3})

# The default value for the Node 'P' and the parameter 'R' are supplied
R = Component("R", {'P': None, 'N': "GND"}, {'R': 1e3})
```

- The component name (e.g. _resistor_, _capacitor_, _nmos_, ...)
- A list containing the names of the nodes or a dictionary containing the name and default values of the nodes. 
- A dictionary containing the name and default values of the parameters.


!!! info
    Keep in mind the order of the nodes and parameters is preserved


### Creating Instances

Once a Component has been created, it can be directly used to spawn new instances thanks to the `new` method. 

```python title="Creating instances from a component"
from nimphel.core import Component

# Nodes can be supplied as a list or as a dictionary
R = Component("R", ['P', 'N'])
R.new(["VDD", "GND"])
R.new(dict(P="VDD", N="GND"))

R = Component("R", {'P': None, 'N': "GND"}, {'R': 1e3})
R.new(dict(P="VDD"))

try:
    R.new({'R': 2e3})
except ValueError:
    print("P has no default value")
```

### Default Values

If a Node or parameter without default value has not been supplied, a `ValueError` is raised. We can exploit this behaviour to mark required values as `None`. That will require us to supply that specific node or parameter when creating the instance. This behaviour can be disabled temporarely through the `check_defaults` keyword.

For more information on how this is implemented, check the function `missing_defaults` in `nimphel.utils`

```python title="Mandatory nodes or parameters"
from nimphel.core import Component

R = Component("R", {'P': 'VDD', 'N': "GND"}, {'R': None})

try:
    R.new()
except ValueError:
    print("We didn't supply the parameter R")

# This one doesn't raise an error
R.new(check_defaults=False)
```

The method `__call__` is an alias for `new` so the following forms are equivalent

```python
R.new(dict(P="VDD"))
R(dict(P="VDD"))
```

### From Instances

It is also possible to create a Component if we already have the desired Instance. Given the instance object, we need to call the `from_instance` classmethod and pass directly the instance. Additionally, the keywords `reset_nodes` and `reset_params` can modify the behaviour when creating the Component:

- If `reset_nodes` is True, all nodes are cleared and set to `None`
- If `reset_params` is True, all params are cleared and set to `None`

```python
inst = Instance("Cap", {'P': 1, 'N': 0}, {"C": 1e-9})

Component.from_instance(inst, reset_nodes=False, reset_params=False)
# Component("Cap", {'P': 1, 'N': 0}, {"C": 1e-9})

Component.from_instance(inst, reset_nodes=True, reset_params=False)
# Component("Cap", {'P': None, 'N': None}, {"C": 1e-9})

Component.from_instance(inst, reset_nodes=False, reset_params=True)
# Component("Cap", {'P': 1, 'N': 0}, {"C": None})

Component.from_instance(inst, reset_nodes=True, reset_params=True)
# Component("Cap", {'P': None, 'N': None}, {"C": None})
```

## Models

Models are a 1 to 1 equivalence of SPICE models. They allow creating new components that inherit from some other components while having different model parameters. The following example shows how to create a model `MOD1` that inherits from `NPN`.

```text title="SPICE model declaration"
model MOD1 NPN (BF=50 IS=1E-13 VBF=50)
```

```python title="Creating a model"
m = Model("MOD1", "NPN", {'BF': 50, 'IS': 1e-13, 'VBF': 50})
```

## Subcircuits

A subcircuit is nimphel is also a 1 to 1 translation of SPICE subcircuits. They allow grouping a number of instances under in order to create a reusable component. Subcircuits, differently from components, need to be registered in a circuit for the simutator to keep track of the different components. This can be accomplished through the `add` method on a `Circuit` object.

Subcircuits are created in a similar fashion as Components.

```python title="Registering a subcircuit"
from nimphel.core import Instance, Subcircuit, Circuit

PMOS, NMOS = Component("PMOS", {}), Component("NMOS", {})

INV = Subcircuit("INV", {"in": None, "out": None, "vdd": "VDD", "gnd": 'GND'})
INV.add(PMOS.new())
INV.add(NMOS.new())

C = Circuit()
C.add(INV)
C.add(INV.new({'in': "INPUT", 'out': "OUTPUT"}))
```

!!! note
    It is important to mention that the circuit registers the state of the subcircuit when it's added. If we modify a subcircuit after it's been registered, the circuit won't be able to see the changes


```python title="Registering a subcircuit"
from nimphel.core import Instance, Subcircuit, Circuit

PMOS, NMOS = Component("PMOS", {}), Component("NMOS", {})

INV = Subcircuit("INV", {"in": None, "out": None, "vdd": "VDD", "gnd": 'GND'})
INV.add(PMOS.new())
INV.add(NMOS.new())

C = Circuit()
C.add(INV)

# We modify the subcircuit
INV.add(PMOS.new())

# We can see that the Circuit is not aware of the new update
C.subcircuits[0] == INV
```

The method `__iadd__` is an alyas to `add` so the following are equivalent

```python
INV.add(PMOS.new())
INV += PMOS.new()
```

## Circuits

In nimphel, circuits are the main interface with SPICE netlists. Directives, Instances and Subcircuits are added to a circuit through the `add` method. A list of elements can be registered in one time by supplying the list directly. 

The `add` method is also overloaded as the `__add__` operator which creates a new copy of the circuit and the `__iadd__` operator which modifies in place.

```python title="Creating a circuit"
from nimphel.core import Circuit, Directive, Instance, Subcircuit

circuit = Circuit()

circuit.add(Directive(...))
circuit.add(Instance(...))
circuit.add(Subcircuit(...))

circuit.add([Instance(...) for i in range(100)])
```

The following [section](readers.md) will show how to parse SPICE netlists to automatically create circuits and write these circuits to a plethora of SPICE specifications or user defined formats.
