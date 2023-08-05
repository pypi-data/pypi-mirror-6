mom-utils
=========


This is a collection of Python utilities for the MOM, a numerical model
developed by GFDL/NOAA


Support and Documentation
-------------------------

Quick howto use
---------------

To install:

    pip install mom-utils

Some uses:

* The input.nml do not require any order, so it is usually not fun to compare two different input.nml. This command is different then a regular diff, since it doesn't care about the order of the variables. The output show what is different, or what is defined in only one of the files.

    mom_namelist compare input.nml input2.nml

* Inside python, one can read an input.nml setup, change one parameter, and write into another input2.nml like this:

    nml_text = open('input.nml', 'r').read()

    cfg = mom_utils.nml_decode(nml_text)

    cfg['ocean_model_nml']['dt_ocean'] = 7200

    output = open('input2.nml', 'w')

    output.write(mom_utils.yaml2nml(cfg))

* Some namelists/parameters changed or disapear between MOM4 and MOM5. The task "check" evaluates if all namelists/parameters in the input.nml are declared in the code.

    mom_namelist check --momsrc=mom/src myexperiments/exp1/input.nml

* Task 4to5 converts a namelist for MOM4 to a namelist for MOM5

    mom_namelist 4to5 input.nml > ./input.nml.new

License
-------

``mom-utils`` is offered under the PSFL.

Authors
-------

Guilherme Castelão <guilherme@castelao.net>
Luiz Irber <luiz.irber@gmail.com>
