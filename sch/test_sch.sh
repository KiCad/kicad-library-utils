#!/usr/bin/bash

# This script file is used to test the consistency of files saved
# from sch python class. Spaces and line positioning will be ignored

if [[ $# < 1 ]]; then
    echo "Usage: $0 sch_files"
    exit 1
fi

function test_sch {
    filename=`basename $1`

# python code --- START
python << EOF
from sch import *
lib = Schematic('$1')
lib.save('/tmp/$filename')
EOF
# python code --- END

    sort "$1" > /tmp/$filename.original.sorted
    sort /tmp/$filename > /tmp/$filename.sch.sorted
    [[ `diff -b /tmp/$filename.original.sorted /tmp/$filename.sch.sorted` ]] && return 0
    return 1
}

for file in "$@"; do
    echo "* testing $file"
    if ( test_sch "$file" ); then
        echo "sch class generated an invalid output file for sch file: $file"
    fi
done
