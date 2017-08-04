#!/usr/bin/env bash

# This script file is used to test the consistency of files saved
# from schlib python class. Spaces and line positioning will be ignored

if [[ $# < 1 ]]; then
    echo "Usage: $0 lib_files"
    exit 1
fi

function test_schlib {
    filename=`basename "$1"`

# python code --- START
python << EOF
from schlib import *
lib = SchLib('$1')
lib.save('/tmp/$filename')
EOF
# python code --- END

    sort "$1" > "/tmp/$filename.original.sorted"
    sort "/tmp/$filename" > "/tmp/$filename.schlib.sorted"
    [[ `diff -b "/tmp/$filename.original.sorted" "/tmp/$filename.schlib.sorted"` ]] && return 0
    return 1
}

# colors
RED="\e[0;31m"
NOCOLOR="\e[0m"

for file in "$@"; do
    echo "* testing $file"
    if ( test_schlib "$file" ); then
        echo -e "${RED}schlib class has generated a non identical output for the file: $file${NOCOLOR}"
    fi
done
