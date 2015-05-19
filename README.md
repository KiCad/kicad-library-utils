#stm32 library generator
This script turns XML files defining pins for STM32 devices into KiCAD libraries

##Running
If you have the correct XML files, just run `main.py path/to/xml path/to/pdfdir`, where `path/to/Xdir` is the path to a directory containing all xml and pdf files. Make sure the XML files have the correct format as there is no error checking.
You need to install [pdfminer](https://github.com/euske/pdfminer) to run this tool!
