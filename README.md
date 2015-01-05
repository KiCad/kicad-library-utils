
KiCad utilities
===============

**schlib.py**: A class to parse components of Schematic Libraries Files Format of the KiCad.


**checklib.py**: This script invokes each checkrule script testing the requested libraries.


**checkrule3_x.py**: Each script checks the correspondent rule and prints out a report informing what is in disagreement with the [KiCad Library Convention](https://github.com/KiCad/kicad-library/wiki/Kicad-Library-Convention).


**fix-pins.py**: This script tests some cases of x/y "wrong" pins positions. The description of the cases are explained in the head of this script file.


How to use
==========

    ./checklib.py path_to_lib1 path_to_lib2
    
    # or run the following command for help
    ./checklib.py -h