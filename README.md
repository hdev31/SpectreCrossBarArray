# CrossbararraySpectre

## Data folder 

This folder contains 10000 input vectors for the first layer of the network and the weights of the layer and biaises for the first layer of the MNIST trained network. 



## nimphel

These scripts are used to generate netlists for Crossbararrays in Spectre with resistances values mapped from weight data and voltages from input vectors. 

These scripts heavily rely on the Nimphel project from https://github.com/servinagrero/nimphel. Please follow instructions there to install the package properly.

Please find at the beginning of each file the parameters you can modify before running them.

### adc.py 

Read positive and negative current files generated by Maestro or ADE L in tran mode and converts it into a list of currents for each row. Creates an histogram for current on each row. *Please note that biais are not modelized in any of the scripts for now values are therefore shown without current that should be added by biases.*

Parameters : 
- positiveCurrentfilepath : positive currents text file
- negativeCurrentfilepath : negative currents text file

Use : python3 adc.py


### inputParsing.py 

Performs digital to analog conversion of the inputs and gives files that contain only an input vectors as voltages.

Parameters : 
- setVoltageup : Maximum positive set Voltage for a RRAM cell
- setVoltagelow : Minimum set Voltage for a RRAM cell
- dacBits : number of bits for DAC conversion
- numberOfInputs : How many vectors should be kept among the 10000
- minNumberOfNonZeroValues : How many Non Zero Values should be in a single input vector (minimum)
- inputfilepath : Input vector data. *Please note that the file has been inverted to facilitate parsing : another script is given to perform this task*
- outputfilepath : file in which the final voltage vectors will be kept

> Use : python3 inputParsing.py

### weightToResistance

Performs weight to resistance conversion from the weight file. The script generates two files for resistances of the positive weights and negative weights. In the positive crossbar, if a negative weight is encountered, resistor value is set to 0 and conversely in negative crossabar. The conversion is done using a scale ranging from 0 to the maximum value encountered during parsing of the input file (maximum of the absolute value). For Process Variability, a value from a Normal distribution N(0, 0.03*(Rmax-Rmin)) is added to each resistance. 

*WARNING : please specify the number of rows of the input file*
Parameters :
- Rmin : Minimum resistance of a RRAM cell
- Rmax : Maximum resistance of a RRAM cell
- processVariability : generate processVariability files ?
- numberOfGenerations : number of processvariability netlists for one single input vector
- sigma : sigma for normal distribution
- rows : how many rows in weights data (do not count biases)
- inputFilePath : Weights on csv format
- resistanceFilePath : File that will contain resistances computed 
- resistanceFilePathNeg : Same but for negative weights
- processVariabilityFilePath : name of files that will contain resistances with process variability -> filenames generated will be as follows -> processvariability*0*.csv ... processvariability*numberOfGenerations*.csv and processvariability_neg_*0*.csv ... processvariability_neg_*numberOfGenerations*.csv

> Use : python3 weightToResistance.py

### mnist_rram

Generates a crossbar array in an Spectre netlist format from an input file and two resistor files (positive and negative weights) and gives a netlist in spectre format. 

*WARNING : please note that columns are not connected to ground : please modify this script if you want to simulate the crossbar without further modifications in Cadence*

> Use : python3 mnist_rram.py input_file resistor_file resistor_negative_file netlist_file

### invertCSV

Simply inverts rows and columns in a csv file. Used for inputs.csv to ease data parsing.

> Use : python3 invertCSV input_file output_file

### generateAllNetlists

Generates all netlist thanks to files generated by other scripts. *Note that this command is very slow due to the use of the subprocess module and the number of netlists*

Parameters :
- netlist_dir : Netlist files directory
- res_dir : Resistances files directory
- input_dir : Input files directory
- process_var_dir : Process variability resistances directory
- numberOfInputs : number of input files
- numberOfProcessVariabilityFiles : number of process variability files

> Use : python3 generateAllNetlists.py

## Simulation

Please see tuto_spectre.md for details on how to simulate a netlist in spectre.