# VQH
Variation Quantum Harmoniser - Sonification tools for VQE


Python dependencies:
`qiskit`

`numpy`

`matplotlib`

`prompt_toolkit`

`python-supercollider` [https://pypi.org/project/supercollider/](https://pypi.org/project/supercollider/)
  - Current `python-supercollider` version 0.0.5 doesn't work on Mac (windows untested) due to a deprecated dependency `pyliblo` and Liblo for OSC. It is also hard to install it on Linux, but it works. I'm working on a solution, migrating the OSC commmutication to `python-osc`, which will be featured in v0.0.6. See this [Pull Request](https://github.com/ideoforms/python-supercollider/pull/12])
