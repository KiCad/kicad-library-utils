#!/usr/bin/env bash

# This script file is used to test the consistency of files saved
# from KicadMod python class. Spaces and line positioning will be ignored

# example of use: ./test_kicad_mod.sh `find /usr/share/kicad/footprints -name *.kicad_mod`

if [[ $# < 1 ]]; then
    echo "Usage: $0 kicad_mod_files"
    exit 1
fi

function format_file {
    # add new line before (
    sed 's/(/\n(/g' < "$1" > "$1.tmp"
    mv "$1.tmp" "$1"

    # add new line before )
    sed 's/)/\n)/g' < "$1" > "$1.tmp"
    mv "$1.tmp" "$1"

    # trim spaces
    sed 's/^ *//;s/ *$//' < "$1" > "$1.tmp"
    mv "$1.tmp" "$1"

    # remove duplicate spaces
    tr -s ' ' < "$1" > "$1.tmp"
    mv "$1.tmp" "$1"

    # remove new lines
    tr -d '\n' < "$1" > "$1.tmp"
    mv "$1.tmp" "$1"

    # add new line before (
    sed 's/(/\n(/g' < "$1" > "$1.tmp"
    mv "$1.tmp" "$1"
}

function test_kicad_mod {
    filename=`basename "$1"`

# python code --- START
python << EOF
from kicad_mod import *
mod = KicadMod('$1')
mod.save('/tmp/$filename.out')
EOF
# python code --- END

    orig="/tmp/$filename.orig"
    out="/tmp/$filename.out"

    cp "$1" "$orig"

    # format files before compare
    format_file "$orig"
    format_file "$out"

    # sort the files
    sort < "$orig" > "$orig.sorted"
    sort < "$out"  > "$out.sorted"

    # print the diff to make easy to debug
    diff -b "$orig.sorted" "$out.sorted"

    # non matching files will remain in tmp directory
    [[ `diff -b "$orig.sorted" "$out.sorted"` ]] && return 0

    # remove the matching files
    rm -f "$orig" "$out" "$orig.sorted" "$out.sorted"
    return 1
}

# colors
RED="\e[0;31m"
GREEN="\e[0;32m"
NOCOLOR="\e[0m"

for file in "$@"; do
    echo "* testing $file"
    if ( test_kicad_mod "$file" ); then
        echo -e "${RED}kicad_mod class has generated a non identical output for the file: $file${NOCOLOR}"
    else
        echo -e "${GREEN}...OK${NOCOLOR}"
    fi
done
