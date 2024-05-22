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


# # Map inputs to DC Voltage (DAC)

# with open(inputfilepath, "r") as finput:
#     listOfInputs = finput.readline().split(",")
#     listOfInputs = [float(i) for i in listOfInputs]
#     # Take only input sets with more than 100 non zero values (arbitrary)
#     numberOfNonZeroValues = 0
#     for i in range(len(listOfInputs)):
#         if(listOfInputs[i] != 0):
#             numberOfNonZeroValues += 1
#     k = 0
#     # Change lines if there is less than 100 non zero values
#     while(k < numberOfInputs):
#         numberOfNonZeroValues = 0
#         while(numberOfNonZeroValues < minNumberOfNonZeroValues):
#             listOfInputs = finput.readline().split(",")
#             listOfInputs = [float(i) for i in listOfInputs]
#             numberOfNonZeroValues = 0
#             for i in range(len(listOfInputs)):
#                 if(listOfInputs[i] != 0):
#                     numberOfNonZeroValues += 1
#             #print(listOfInputs)
#             # Quantization
#             listOfInputs = [int(i*(2**(dacBits) - 1)) for i in listOfInputs]
#             #print(listOfInputs)
#             # Mapping 
#             listOfInputs = [(i/(2**(dacBits) - 1)) * (setVoltageup - setVoltagelow) + setVoltagelow for i in listOfInputs]
#             #print(listOfInputs)
#         # Append to an input file
#         outputfilepathcurr = outputfilepath + "_" + str(k) + ".csv"
#         with open(outputfilepathcurr, "w+") as f1:
#             listOfInputs = [str(i) for i in listOfInputs]
#             f1.write(','.join(listOfInputs) + "\n")
#         f1.close()
#         k += 1
# finput.close()

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
            
            




