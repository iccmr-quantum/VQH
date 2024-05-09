# VQH
Variation Quantum Harmonizer - Sonification Methods for the VQE, or the VQE as a musical interface.

## Description
The Variational Quantum Harmonizer (VQH) is a sonification project aimed at quantum algorithms. Additionally, VQH is a command-line interface tool for sonifying the Variational Quantum Eigensolver algorithm. It is also a digital musical interface, enabling artists to flexibly control/design QUBO cost functions that, being optimized by means of a variational quantum algorithm, will generate data that can be sonified in real time.

The VQH interface allows the quick access for simulation and sonification of VQE in a "live-coding" performace setup. Provided access, you can also run the VQE algorithm using real IBMQ or IQM hardware

You can find more information in our publication on the ISQCMC symposium: 
[Variational Quantum Harmonizer: Generating Chord Progressions and other Sonification Methods with the VQE Algorithm](https://doi.org/10.5281/zenodo.10206731)

You can listen to music that has used the VQH in its artistic process:
[Dependent Origination (2023)](https://www.youtube.com/playlist?list=PLZcA8yDT3f3YLiVGQOuWJrHmD7R1T4Tn-) [Hexagonal Chambers (2023-24)](https://youtu.be/3FZZJFP96CQ?si=dYiKHtvZLthsXz4J&t=1580)


## Installation

- Clone This repository

- Create a python environment (>3.10 recommended)

Python dependencies:
`qiskit`, `qiskit-optimization`, `qiskit-aer`, `qiskit-iqm`, `iqm-cortex-cli`, `numpy`, `matplotlib`, `PyQt5`, `prompt_toolkit`, `python-osc`, [`python-supercollider`](https://pypi.org/project/supercollider/)

Installing dependencies with pip:

```bash
pip install qiskit qiskit-optimization qiskit-aer qiskit-iqm iqm-cortex-cli numpy matplotlib pyqt5 prompt_toolkit python-osc supercollider
```


If you are sonifying your data with SuperCollider, you should also [download and install it](https://supercollider.github.io/downloads.html)


## Basic usage

### Running the main script

VQH is a prompt-based CLI interface. Within your python environment, you can run a VQE experiment session through the main script `VQH.py` and using some flags, as described below.

`python VQH.py [SESSIONPATH] [PLATFORM] [PROTOCOL]`


The flags in square brackets [] are optional, but it is recommended that you set up a personalised `sessionpath`.

*Flag description*:

	`sessionpath` - The name of the folder where the VQE experiments and all generated data will be stored. Default is "Session".
	`platform` - Quantum Platform/Provider used. Available platforms are `local` (qiskit_aer), `iqm` and `ibm`. You should setup the platform with your own credentials. Default is `local`.
	`protocol` - Note encoding schemes/protocols for interpreting quantum states as notes, determining how VQE will be sonified. Available protocols are `harp` (default). New protocols are being introduced.
	
#### Example

`python VQH.py Example local`

The following command will start VQH, all generated data will be stored inside a folder named `Example_Data/`, will use the local simulator, and the `harp` protocol as default:


### VQH internal functions
Once `VQH.py` starts, you will be presented with a prompt "` VQH=>`", where you can call internal commands for different purposes:

	`runvqe` - This is the main command. It looks at the current VQE configuration files and current status of the QUBO matrix (no need to restart the program) and runs the VQE according to specification, saving the results and configs used into a subfolder with a given *path_id*, or the experiment's unique index.
	`play [type]` - Triggers the SuperCollider sonification. Tye [type] flag denotes the sonification method used (additive, subtractive, etc). Check below for the specification of each sonification type. If unsure, just use `play 1`
	`playfile [index] [type]` - Same as above, but sonifies a file stored in your session folder. Parse any stored experiment by using the subfolder's index number.
	`stop` - Kills all playing sounds. Necessary for some sonification types.
	`quit` or just `q` - Exits the program.
	

### Sonifying with SuperCollider

#### Setup
*On the First time* you use VQH, There won't be any pre-compiled synthesizers yet. For that, you need to _store_ the SuperCollider SynthDefs located in the `synth/synthdefs/vqe_sonification.scd` and other `*.scd` files if needed. (Feel free to customize and create your own synthdefs, as long as you use the same name/key for the respective sonification type).

- To compile the synthdefs, open `synth/synthdefs/vqe_sonification.scd`, click inside the region inside a SynthDef (such as `\vqe_model1_son1`) and press `CTRL(CMD) + Enter`, which will run the `.store` command after the SynthDef.

_If you have done this at least once, you can proceed directly to the next step._

- Boot a default SuperCollider server (`s.boot`)

#### Sonification Types
Refer to the [paper](https://doi.org/10.5281/zenodo.10206731) for a more detailed description on some of the sonification types.


	`1` - Additive Synthesis (12 Qubits) [supercollider]
	`2` - Additive Synthesis (8 Qubits) [supercollider]
	`3` - Arpeggios [supercollider]
	`4` - Hexagonal Chambers' Book [zen]
	
	
### Sonifying with Zen

Each session folder contains a subfolder called `to_pete`. The latest sonification data is stored in a file `dependent_origination.json`. 

If you want to use this data on Zen, there are two options. You either host your own clone of [ct-samples](https://github.com/cephasteom/ct-samples), and keep updating your dataset by hand (not recommended) OR

You copy/paste all contents inside the template folder `to_pete_template`, where you can host the file by using `npm run serve`. (Make sure to have Node >16 installed). In addition, you may need to generate a custom `.pem` certificate to allow zen to make `https` connections, specially if Zen is running on a separate machine.

### Designing QUBOs and Configuring the VQE parameters

Apart from `VQH.py`, there are _two_ other important files for the VQH workflow:

	- `h_setup.csv` Contains a QUBO matrix, which follows a specific format
		QUBO matrices should be exactly as the one below.
		The header should contain the matrix name and note labels.
		NO SPACE between commas for header and labels!
		Spaces allowed only for coefficients. See `h_setup-Example.csv`
    
		h1,label1,label2,label3,...,labeln
		label1,c11,c12,c13,...,c1n
		label2,c21,c22,c23,...,c2n
		label3,c31,c32,c33,...,c3n
		...
		labeln,cn1,cn2,cn3,...,cnn
		h2,label1,label2,label3,...,labeln
		label1,c11,c12,c13,...,c1n
		

## Contributing

To assist with potentioal contributions, here a schematic of the software structure and main object hierarchies for the lates version.

### Code structure

![VQH Software Structure](https://github.com/iccmr-quantum/VQH/assets/28213905/9a019a5c-7c76-4c5a-babe-7ebac7a162ce)

