import numpy as np

# Values of maximal and minimal resistance
Rmin = 1e4
Rmax = 1e6


# Process variability 
processVariability = True
numberOfGenerations = 20
sigma = 0.03*(Rmax - Rmin)


# Number of rows
rows = 784

# Filepath for input data :
inputFilePath = "../data/weights.csv"
# Filepath for resistance data :
resistanceFilePath = "./RESISTANCES/resistances.csv"
# Filepath for negative weights resistances :
resistanceFilePathNeg = "./RESISTANCES/resistances_neg.csv"
# Process variability base file path : (files will be named from filepath_0 to filepath_numberOfGenerations)
processVariabilityFilePath = "./RESISTANCES/processvariabiliy" 


# CODE ---------------------------------------------------------------------


# Need to normalize weight
max_weights_positive = 0
min_weights_negative = 0
with open(inputFilePath, "r") as f1:
    for i in range(rows): # Iteration on inputs and then on columns
        listOfWeights = f1.readline().split(",")
        listOfWeights = [float(i) for i in listOfWeights]
        for j in range(len(listOfWeights)):
            max_weights_positive = max(max_weights_positive, listOfWeights[j])
            min_weights_negative = min(min_weights_negative, listOfWeights[j])
f1.close()

print("Minimum weight = " + str(min_weights_negative) + "and maximum weight = " + str(max_weights_positive))


# In order to determine the maximum weight whether it is positive or negative : positive and negative weights uses the same scale for conversion
max_weights = max(max_weights_positive, (-1)*min_weights_negative)


# Linear transform (0 -> Rmax, MAXIMUM WEIGHT -> Rmin)

def weightToResistance(value,Rmin, Rmax, max_weights): 
    if(value > 0):
        return (Rmin - Rmax)*value/max_weights + Rmax
    else:
        return (-1)*((Rmin - Rmax)*(-1)*value/max_weights + Rmax)

# Writes resistances in another file to simplify netlist generation script

with open(inputFilePath, "r") as f2:
    with open(resistanceFilePath, "w+") as f3:
        with open(resistanceFilePathNeg, "w+") as f4:
            for i in range(rows): # Iteration on inputs and then on columns
                listOfWeights = f2.readline().split(",")
                listOfWeights_neg = listOfWeights[:]
                # print("Valeur avant conversion : " + listOfWeights[0])
                listOfWeights = [float(i) for i in listOfWeights]
                listOfWeights = [weightToResistance(j, Rmin, Rmax, max_weights) for j in listOfWeights]
                # This part is useful to separate positive and negative weights
                for k in range(len(listOfWeights)):
                    if(listOfWeights[k] > 0):
                        listOfWeights_neg[k] = 0
                    else:
                        listOfWeights_neg[k] = (-1)*listOfWeights[k]
                        listOfWeights[k] = 0
                listOfWeights = [str(j) for j in listOfWeights]
                listOfWeights_neg = [str(j) for j in listOfWeights_neg]
                # print("Valeur après conversion : " + listOfWeights[0])
                f3.write(",".join(listOfWeights) + "\n")
                f4.write(",".join(listOfWeights_neg) + "\n")

f2.close()
f3.close()



if(processVariability == True):
    for i in range(numberOfGenerations):
        filepath = processVariabilityFilePath + str(i) + ".csv"
        with open(filepath, "w+") as fp:
            with open(resistanceFilePath, "r") as fp1:
                    for i in range(rows): 
                        listOfWeights = fp1.readline().split(",")
                        listOfWeights = [float(i) for i in listOfWeights]
                        # Adds a resistance to the precedent resistance to simulate process variability
                        # Puts 0 if no resistance is needed (negative weights)
                        listOfWeights = [((j + np.random.normal(0, sigma)) if j > 0 else 0) for j in listOfWeights]
                        listOfWeights = [str(j) for j in listOfWeights]
                        # print("Valeur après conversion : " + listOfWeights[0])
                        fp.write(",".join(listOfWeights) + "\n")
            fp1.close()
        fp.close()
    for i in range(numberOfGenerations):
        filepath = processVariabilityFilePath + "_neg_" + str(i) + ".csv"
        with open(filepath, "w+") as fp:
            with open(resistanceFilePathNeg, "r") as fp1:
                    for i in range(rows): 
                        listOfWeights = fp1.readline().split(",")
                        listOfWeights = [float(i) for i in listOfWeights]
                        # Adds a resistance to the precedent resistance to simulate process variability
                        listOfWeights = [((j + np.random.normal(0, sigma)) if j > 0 else 0) for j in listOfWeights]
                        listOfWeights = [str(j) for j in listOfWeights]
                        # print("Valeur après conversion : " + listOfWeights[0])
                        fp.write(",".join(listOfWeights) + "\n")
            fp1.close()
        fp.close()
