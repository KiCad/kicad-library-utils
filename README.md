# STM32 library generator
This script turns XML files defining pins for STM32 devices into KiCAD libraries

## Prerequisites
* XML files, taken from STM32CubeMX install (from db/mcu folder)
* XML files for obsolete devices (currently STM32F050xx and STM32F313xx), which
  can be taken from STM32CubeMX install (archives in olddb folder)
* Datasheet PDFs, downloaded from ST's website, current (21.02.2016) list could 
  be found in datasheets.txt
* [pdfminer](https://github.com/euske/pdfminer) tool

## Running
If you have the correct XML files, just run `main.py path/to/xml path/to/pdfdir`, 
where `path/to/Xdir` is the path to a directory containing all xml and pdf files. 
Make sure the XML files have the correct format as there is no error checking.
