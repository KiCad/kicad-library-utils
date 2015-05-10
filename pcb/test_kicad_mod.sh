#!/usr/bin/bash

# This script file is used to test the consistency of files saved
# from KicadMod python class. Spaces and line positioning will be ignored

if [[ $# < 1 ]]; then
    echo "Usage: $0 kicad_mod_files"
    exit 1
fi

function test_kicad_mod {
    filename=`basename "$1"`

# python code --- START
python << EOF
from kicad_mod import *
mod = KicadMod('$1')
mod.save('/tmp/$filename.out')
EOF
# python code --- END

    # remove spaces and new lines, re-add some new lines and sort the file
    tr -d ' \n' < "$1" | tr '(' '\n(' | sort > "/tmp/$filename.original.sorted"
    tr -d ' \n' < "/tmp/$filename.out" | tr '(' '\n(' | sort > "/tmp/$filename.out.sorted"

    [[ `diff -b "/tmp/$filename.original.sorted" "/tmp/$filename.out.sorted"` ]] && return 0
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
