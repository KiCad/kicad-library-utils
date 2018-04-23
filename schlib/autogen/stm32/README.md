# STM32 library generator

This script generates KiCad symbol libraries from XML files defining pins for
STM32 devices.

## Prerequisites

* XML files, taken from STM32CubeMX install (from db/mcu folder).
* Datasheet PDFs, downloaded from ST's website.  A current list as of
  2018-02-06 can be found in datasheets.txt.  These PDFs can be downloaded all
  at once with `wget -P datasheets -ci datasheets.txt`.
* [pdfminer](https://github.com/euske/pdfminer) tool.

## Running

If you have the correct XML files, just run
`./stm32_generator.py xmldir pdfdir`, where `xmldir` is a directory containing
all the necessary XML files, and `pdfdir` is a directory containing all the PDF
files.  Make sure the XML files have the correct format as there is no error
checking.
