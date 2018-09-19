# mrn
A couple of scripts used in my final year research project in mechanical engineering at the University of Pretoria.


## Background
The Python scripts were used run FEM simulations of an indentation test in CalculiX, and then process and analyse the results of the simulations. Two of the main forms of numerical analyses performed were:
* Optimsation analysis using gradient-base optimisation and RBF surrogate models with [SciPy](https://www.scipy.org/),
* PLS statistical regression with [scikit-learn](http://scikit-learn.org/).


The final report on the work was titled

> Numerical Investigation on Methods and Models for Material Identification Using Spherical Indentation

You can find a PDF of the report [here](https://github.com/nickkossolapov/mrn/blob/master/final_report.pdf)


I also published a conference paper based on this report, published in the Proceedings of the Eleventh South African Conference on Computational and Applied Mechanics (SACAM 2012) and co-authered by Prof. Schalk Kok, titled

> On the uniqueness of material identification for aluminium using spherical indentation

You can find a PDF of the paper [here](https://github.com/nickkossolapov/mrn/blob/master/sacam_paper.pdf)


## Usage
To be used with [CalculiX 2.11+](http://www.calculix.de/), with GraphiX used to generate the geometries.

```mrn.py``` is the entry point for running and processing simulations. The other Python files are libraries for functions to pre-process and post-process the files, as well as generate any inputs. The script must be executed inside bConverge's CalculiX Command cmd to ensure the environment variables are correctly configured, or ```run_ccx``` in ```simulation.py``` should be modified appropriately.

```pre.fbd``` files is a GraphiX cgx script, which is used to generate the geometry and mesh.
