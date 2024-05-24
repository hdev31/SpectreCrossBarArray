import matplotlib.pyplot as plt
import numpy as np


positiveCurrentfilepath = "./CURRENTS/positivecurrent.txt"
negativeCurrentfilepath = "./CURRENTS/negativecurrent.txt"


# Stores current values in order from COL_000 to COL_099 in a list

with open(positiveCurrentfilepath, "r", encoding="utf8") as f1:
    f1.readline()
    f1.readline()
    f1.readline()
    f1.readline()
    f1.readline()
    poscurrent = f1.readline()

listOfPositiveCurrentString = poscurrent.split()
listOfPositiveCurrentString.pop(0)

listOfPositiveCurrent = []

for i in listOfPositiveCurrentString:
    listOfPositiveCurrent.append((-1)*float(i))

print(listOfPositiveCurrent)

# Stores current values in order from COLN_000 to COLN_099 in a list

with open(negativeCurrentfilepath, "r", encoding="utf8") as f1:
    f1.readline()
    f1.readline()
    f1.readline()
    f1.readline()
    f1.readline()
    poscurrent = f1.readline()

listOfNegativeCurrentString = poscurrent.split()
listOfNegativeCurrentString.pop(0)

listOfNegativeCurrent = []

for i in listOfNegativeCurrentString:
    listOfNegativeCurrent.append(float(i))

print(listOfNegativeCurrent)

# Computes the value of each column current

listOfCurrent = []
for i in range(len(listOfPositiveCurrent)):
    listOfCurrent.append(listOfPositiveCurrent[i] + listOfNegativeCurrent[i])

print(listOfCurrent)

# Histogramme pour tous les courants sur toutes les colonnes sans et avec process variability
# Et un histogramme sur chaque colonne avec process variability 

plt.bar([i for i in range(100)],listOfCurrent)
plt.title("Courants sur chaque colonne")
plt.xlabel("Numéro de colonne")
plt.ylabel("Courant (A)")
plt.show()

