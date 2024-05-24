# Digital to analog conversion
# Sets the upper and the lower bounds of the set Voltage to stay in read region 
setVoltageup = 3
setVoltagelow = -3
dacBits = 10

# Number of different non zero input sets 
numberOfInputs = 20
# Minimum number of non zero inputs in a single vector
minNumberOfNonZeroValues = 100

# All vectors with null vectors
inputfilepath = "../data/inputs_inverted.csv"

# Final base filepath with only a few vectors non null (inputs will be stored in files named inputs_0 to inputs_numberOfInputs)
outputfilepath = "./INPUTS/inputs"



with open(inputfilepath, "r") as finput:
    k = 0
    for line in finput:
        if(k < numberOfInputs):
            line = line.split(",")
            line = [float(j) for j in line]
            numberOfNonZeroValues = 0
            for j in line:
                if (j != 0):
                    numberOfNonZeroValues += 1
            if(numberOfNonZeroValues > minNumberOfNonZeroValues):
                # Quantization
                line = [int(i*(2**(dacBits) - 1)) for i in line]
                # Mapping
                line = [(i/(2**(dacBits) - 1)) * (setVoltageup - setVoltagelow) + setVoltagelow for i in line]
                # Generate new file
                outputfilepathcurr = outputfilepath + "_" + str(k) + ".csv"
                # Write to file
                with open(outputfilepathcurr, "w+") as f1: 
                    line = [str(i) for i in line]
                    f1.write(','.join(line) + "\n")
                f1.close()
                k += 1
        
finput.close()
            
            




