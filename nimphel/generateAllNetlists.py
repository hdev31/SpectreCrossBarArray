import subprocess

# DIRECTORIES

netlist_dir = "./NETLISTS"
res_dir = "./RESISTANCES"
input_dir = "./INPUTS"
process_var_dir = "./NETLISTS/PV"

# PARAMETERS

numberOfInputs = 20
numberOfProcessVariabiliyFiles = 20

# Generates 20 netlists with the same resistor crossbar (no process variability)
for i in range(numberOfInputs):
    result = subprocess.call(["python3", "mnist_rram.py", input_dir + "/" + "inputs_" + str(i) + ".csv", res_dir + "/" + "resistances" + ".csv", res_dir + "/" + "resistances_neg" + ".csv", netlist_dir + "/netlist_no_PV" + str(i)])

# Generates for each input file 20 crossbar with different resistor values due to process variability

for i in range(numberOfInputs):
    for j in range(numberOfProcessVariabiliyFiles):
        result = subprocess.call(["python3", "mnist_rram.py", input_dir + "/" + "inputs_" + str(i) + ".csv", res_dir + "/" + "processvariabiliy" + str(j) + ".csv", res_dir + "/" + "processvariabiliy_neg_" + str(j) + ".csv", process_var_dir + "/netlist_input_" + str(i) + "res_" + str(j)])
