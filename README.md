
KiCad utilities
===============

## schlib directory

**schlib.py**: A python class to parse Schematic Libraries Files Format of the KiCad.


**checklib.py**: Such script invokes each checkrule script testing the requested libraries.


**checkrule3_x.py**: Each checkrule script checks your correspondent rule and prints out a report informing what is in disagreement with the [KiCad Library Convention](https://github.com/KiCad/kicad-library/wiki/Kicad-Library-Convention).


**fix-pins.py**: Such script was created in order to help the adaptation of the already existing library files to the KiCad Library Convention. It tests some cases of x/y "wrong" pins positions and try to fix them if they pass in the checking of some prerequisites. The description of the cases are explained in the head of the script file.

**test_schlib.sh**: A shell script used to validate the generation of files of the schlib class.

## sch directory

**sch.py**: A python class to parse Schematic Files Format of the KiCad.

**test_sch.sh**: A shell script used to validate the generation of files of the sch class.


How to use
==========

## Schematic Library Checker

    cd schlib
    ./checklib.py path_to_lib1 path_to_lib2
    
    # or run the following command for help
    ./checklib.py -h
