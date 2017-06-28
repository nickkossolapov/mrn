# mrn
Software environment for final year engineering project.

Project title: "Determining the stress-strain curve of aluminium using an indendation test"

To be used with CalculiX 2.11 (with GraphiX).


```mrn.py``` the primary script for running simulations. The other Python files are libraries for functions to pre-, and post-process the files, as well as generate any inputs. Must be executed using bConverge's CalculiX Command cmd, or ```run_ccx``` in ```simulation.py``` should be modified appropriately.

```pre.fbd``` files is a cgx script, which is used to generate the geometry and mesh