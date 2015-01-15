#!/usr/bin/bash

# This script file is used to test the consistency of files saved
# from schlib python class. Spaces and line positioning will be ignored

if [[ $# < 1 ]]; then
    echo "Usage: $0 libfiles"
    exit 1
fi

function test {
    filename=`basename "$1"`

# python code --- START
python << EOF
from schlib import *
lib = SchLib('$1')
lib.save('/tmp/$filename')
EOF
# python code --- END

    sort $1 > /tmp/$filename.original.sorted
    sort /tmp/$filename > /tmp/$filename.schlib.sorted
    [[ `diff -b /tmp/$filename.original.sorted /tmp/$filename.schlib.sorted` ]] && return 0
    return 1
}

for file in $@; do
    if ( test "$file" ); then
        echo "schlib created an invalid output file for libfile: $file"
    fi
done
