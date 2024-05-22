#!/usr/bin/env python3

from nimphel.core import *
from nimphel.readers import *
from nimphel.writers import *
import numpy as np
from itertools import product

# Constants
rows = 10
cols = 10

# Nets for the first 
nets_in = [f"IN_{i:03d}" for i in range(rows)]
nets_col = [f"COL_{i:03d}" for i in range(cols)]
files = [f'"./INPUT_{i:03d}.txt"' for i in range(rows)]
corner_file = "/home/users/vinagres/projet_cmos065_58/corners.scs"

# Components
Vsource = Component("vsource", ["VDD", "GND"], {"type": "pwl"}, cap="V")
Mem = Component("resistor", ["P", "N"], {})

circuit = Circuit()

# netlistHeader
circuit += Directive("simulator", lang="spectre")
circuit += Directive("global 0 gnd!")
circuit += Directive(f'include "{corner_file}"')

# Digital to analog conversion
# Sets the upper and the lower bounds of the set Voltage to stay in read region 
setVoltageup = 3
setVoltagelow = -3
dacBits = 10


#Ici, il faudra mettre en source dc toutes les entrées avec la bonne tension

#with open("./INPUT_000.txt", "w+") as fp:
#    for i in np.arange(setVoltagelow, setVoltageup, 1/(2**10)):
#        fp.write(f"{interval*timesteps:02d}u" + f" {i:f}\n")
#        timesteps += 1



 
# circuit.add(
#     [
#         Vsource.new(dict(VDD=i, GND=0), params={"file": f})
#         for i,f in zip(nets_in, files)
#     ]
# )

# Pour l'instant :
circuit.add(
    [
        Vsource.new(dict(VDD=i,GND=0), params={"dc": 1}) for i in nets_in
    ]
)



for i, o in product(nets_in, nets_col):
    r = np.random.uniform(1e4, 1e6, 1) 
    inst = Mem.new(dict(P=i, N=o), params={"r": r[0]})
    circuit.add(inst)

# Sense amplifiers
#ADC = Component("ADC", ["IN", "OUT"], {}, cap="I")

#for i, c in enumerate(nets_col):
#    inst = ADC.new(dict(IN=c, OUT=f"ADC_{i:03d}"))
#    circuit.add(inst)

writer = SpectreWriter()
netlist = writer.dump(circuit)
print(netlist)

with open("spectre_netlist", "w+") as fp:
    writer.dump_to_file(circuit, fp)
    fp.write("\n")

fp.close()