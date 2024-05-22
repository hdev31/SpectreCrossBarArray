# Writers

Writers allow the conversion of an element into a plethora of file formats to use the same element under different SPICE implementations or other tools. Although writers are focused on outputing SPICE netlists files, they can be used to export a Circuit to any user defined format.

## Exporting a circuit

Once a circuit has been generated, it can be exported to a string, and consequently to a file, by using the provided `Writer` class. The method `dump` converts the circuit into a string, while the `dump_to_file` method writes the element directly to the file given the path.

```python title="Exporting a circuit"
writer = CustomWriter()

# Write the circuit into a string
res = writer.dump(circuit)

# Write the circuit directly into a file
with open("/path/to/file", "w+") as fp:
    writer.dump_to_file(circuit, fp)
```

## Custom Writers

As of today, the following writers are implemented: `Spectre`.

However, more writers can be implemented easily by creating a class that inherits from the `Writer` class. To define the format for a given object (instance, subcircuit, directive, ...) the user needs to implement a method whose name corresponds to the desired object. If a method is not implemented for a given type of object, the `Writer` will use the `__default__` method that outputs the string representation of the object. This method can also be overwritten.

The following example shows how to serialize a circuit into the JSON format. In this case, creasing a custom class just to call the `json.dumps` method is a bit convoluted, but it shows that is possible to preprocess a circuit before the serialization.

```python title="Defining a custom writer"
import json

class CustomWriter(Writer):
    def instance(self, o):
        return json.dumps(dict(o))

    def directive(self, o):
        return json.dumps(dict(o))

    def subcircuit(self, o):
        return json.dumps(dict(o))
```

Once a writer has been defined, the user needs to create an instance and call either the `writes` or `write` method. The first one, outputs circuit converted into a string, while the latter writes the string directly into the supplied path.

# Deserializing a circuit

Writers allow converting a circuit into a plethora of SPICE formats or user defined text formats. However, a problem arises when we want to serialize a circuit into a given format (e.g JSON). This can be achieved by overwriting the `writes` method to directly serialize the object to the given format. As the `write` method automatically calls `writes` it may not be necesary to override both methods.

The deserialization process is described in detail in the [parsing](parsers.md) section

