#!/usr/bin/env python3

from nimphel.core import *
from nimphel.readers import *
from nimphel.writers import *
from itertools import product
import argparse

parser = argparse.ArgumentParser(description="Generate a crossbar array from an input file and a resistor file to a netlist file")

parser.add_argument('input_file', type=str, help="File containing the INPUTS for the crossbar")
parser.add_argument('resistor_file', type=str, help="File containing the positive resistors for the crossbar")
parser.add_argument('resistor_neg_file', type=str, help="File containing the 'negative' resistors for the crossbar")
parser.add_argument('netlist', type=str, help="Filepath to netlist")

args = parser.parse_args()

# Only on first layer of the network 
rows = 784
cols = 100

# Nets for the first crossbar (positive weights)
nets_in = [f"IN_{i:03d}" for i in range(rows)]
nets_col = [f"COL_{i:03d}" for i in range(cols)]

# Nets for the second crossbar (negative weights)
nets_col_neg = [f"COLN_{i:03d}" for i in range(cols)]

# Components
Vsource = Component("vsource", ["VDD", "GND"], {"type": "pwl"}, cap="V")
Mem = Component("resistor", ["P", "N"], {})
circuit = Circuit()

# netlistHeader
circuit += Directive("simulator", lang="spectre")
circuit += Directive("global 0 gnd!")

# For whatever reason, it is impossible to descend into hierarchy to get signals that's why
# I add them as input/output of a symbol
listOfNets = ""
for i in nets_col:
    listOfNets += " "
    listOfNets += i
for j in nets_col_neg:
    listOfNets += " "
    listOfNets += j
circuit += Directive("subckt mnist_grid" + listOfNets)


with open(args.input_file, "r") as fin:
    line = fin.readline().split(",")
    line = [float(j) for j in line]
    for i in range(len(nets_in)):
        circuit.add(Vsource.new(dict(VDD=i, GND=0), params={"dc": line[i]}))
fin.close()

# circuit.add([Vsource.new(dict(VDD=i,GND=0), params={"dc": 1}) for i in nets_in])




# with open("../data/weights.csv", "r") as f1:
#     for i in nets_in: # Iteration on inputs and then on columns
#         listOfWeights = f1.readline().split(",")
#         listOfWeights = [float(i) for i in listOfWeights]
#         for o in range(len(nets_col)):
#             # print(weightToResistance(listOfWeights[o], Rmin, Rmax))
#             inst = Mem.new(dict(P=i, N=nets_col[o]), params={"r" : weightToResistance(listOfWeights[o], Rmin, Rmax)})
#             circuit.add(inst)

# f1.close()

with open(args.resistor_file, "r") as fr:
    for i in nets_in:
        listOfResistances = fr.readline().split(",")
        listOfResistances = [float(j) for j in listOfResistances]
        for o in range(len(nets_col)):
            if(listOfResistances[o] != 0): # Do not place a resistor if there is a negative weight at this index
                inst = Mem.new(dict(P=i, N=nets_col[o]), params={"r" : listOfResistances[o]})
                circuit.add(inst)
fr.close()

with open(args.resistor_neg_file, "r") as frneg:
    for i in nets_in:
        listOfResistances = frneg.readline().split(",")
        listOfResistances = [float(j) for j in listOfResistances]
        for o in range(len(nets_col_neg)):
            if(listOfResistances[o] != 0): # Do not place a resistor if there is a negative weight at this index
                inst = Mem.new(dict(P=i, N=nets_col_neg[o]), params={"r" : listOfResistances[o]})
                circuit.add(inst)
frneg.close()



    


# for i, o_neg in product(nets_in, nets_col_neg):
#     # Adds a 10 % process variability to the resistor value
#     r = np.random.uniform(Rmin, Rmax, 1) 
#     inst = Mem.new(dict(P=i, N=o_neg), params={"r": r[0] + np.random.uniform(0, 0.1*(Rmax-Rmin), 1)[0]})
#     circuit.add(inst)

writer = SpectreWriter()

with open(args.netlist, "w+") as fp:

    writer.dump_to_file(circuit, fp)
    fp.write("\n")
    fp.write("ends mnist_grid")

fp.close()

