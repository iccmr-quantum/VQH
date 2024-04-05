# Temporary API reference for VQH functions

## Workflow for Harp (QUBO + Marginal) model

1- CSV File -> QUBO -> Ising Hamiltonian -> PauliSum Operators

2- Operators + Anzats + Optimizer -> Sampling VQE

3- VQE Sample/Iteration -> Statevector Binary Probabilities (SBP) + Expectation Value (EV) 

4- SBP -> Marginal Distribution (MD) -> Loudness

5- After all iterations: Loudnesses with Print Format (Dict of Lists) -> Loudnesses with Sonification Format (List of Dicts) 

6- Data in Print Format -> Plot

7- Save all Data and Metadata to Experiment subfolder

8- Data in Sonification Format -> Sonification Mapping -> Synth -> :)


`harp.py` Methods' partial docstrings

`build_qubos_from_csv()`
Description: Gets a csv file, containing a single or a set of matrices (check the appropriate matrix formating) and builds a QUBO (or QUBOS) from it.
Input: CSV Matrices
Output: QUBOS
Needs Modification for Amplitude? YES
Is there a separate function implemented for this already? YES

`H_Ising()`
Description: For Classical computation. 
Needs Modification for Amplitude? NO

`qubo_to_operator()`
Description: Translates the QUBO problem into a set of Pauli Operators. First, It computes the Ising Hamiltonian, then obtains the operators.
Input: QUBO(s)
Output: PauliSumOp (Hamiltonian in qubit format) 
Needs Modification for Amplitude? YES
Is there a separate function implemented for this already? YES

`return_optimizer()`
Description: Selects a classical optimizer based on the `vqe_conf.json` file
Needs Modification for Amplitude? NO

`run_sampling_vqe()`
Description: Runs the VQE, and also Samples the intermediate statevectors for each VQE iteration.
Inputs: Ansatz, PauliSumOp, Optimizer, Initial condition
Outputs: Raw Results, Set of Binary Probabilities (SBP), Set of Expectation Values (List)
Needs Modification for Amplitude? NO

`binary_probabilities_to_loudness()`
Description: Computes the Marginal Probabilities from the SBP
Inputs: Set of SBP
Outputs: Set of Marginal Probabilities, e.g. Loudnessess, e.g. Print Format
Needs Modification for Amplitude? NO, IGNORE
Is there a separate function implemented for this already? NO, MAKE SURE THE SET OF BINARY PROBABILITIES ARE IN PRINT FORMAT

`loudnesses_to_list_of_dicts()`
Description: Print Format to Sonification Format
Input: Loudnesses (Print Format)
Output: Loudnesses (Sonification Format)
Needs Modification for Amplitude? NO

`compute_exact_solution()`
Description: Exactly what the name says.
Input: PauliSumOp
Output: Expectation Value result using Numpy
Needs Modification for Amplitude? NO, IGNORE

`harmonize()`
Warning: this is a mess
Description: main function for running vqe. From QUBO, to Ansatz, to Optimizer, runs the Sampling VQE, Computes exact solution for comparison, gets marginal distributions, print and sonification formats.
Input: QUBOS and VQE conf
Output: Data in Sonification Format
Needs Modification for Amplitude? YES
Is there a separate function implemented for this already? NO

`plot_values()`
Description: PLOT
Input: Exp. Values in Print Format (it already is)
Needs Modification for Amplitude? NO, IGNORE

`plot_loudness()`
Description: PLOT
Input: Loudnesses in Print Format
Needs Modification for Amplitude? NO, IGNORE

`run_vqh()`
Warning: This is a mess.
Description: MAIN LOOP. It deals mainly with files and dataset organization, and runs everything related to VQE and encoders. This is also where special connections (e.g. sonification with Zen) happens.
Input: Main folder name
Output: Data in Sonification Format
Description 2: It goes in the folder, gets the QUBO from the csv, runs `harmonize`, plots and saves the results in a subfolder for later sonification.
Needs Modification for Amplitude? YES, Call the right functions, and also COMMENT out everything inside the `# Dependent Origination related code----` section
Is there a separate function implemented for this already? NO

`compute_exact_solution()`
Warning: DUPLICATED

`class HarpProtocol(VQHProtocol)`
Description: This class is how this file and implementations are connected with the rest of the code, enabling us to switch between encoding schemes. See the file `protocol_library.py`. For now, the only thing that it does is to call the `run_vqh()` function, and then parse the data results (in Sonification format) back to the CLI interface. 
Needs Modification for Amplitude? NOT NOW
Is there a separate function implemented for this already? YES, called `AmplitudeProtocol`


## Workflow for Amplitude (Hamiltonian + Amplitude) model

1- CSV File -> Hamiltonian -> PauliSum Operators
2- Operators + Anzats + Optimizer -> Sampling VQE
3- VQE Sample/Iteration -> Statevector Binary Probabilities (SBP) + Expectation Value (EV) 
4- SBP -> Loudness
5- After all iterations: Loudnesses with Print Format (Dict of Lists) -> Loudnesses with Sonification Format (List of Dicts) 
6- Data in Print Format -> Plot
7- Save all Data and Metadata to Experiment subfolder
8- Data in Sonification Format -> Sonification Mapping -> Synth -> :)
