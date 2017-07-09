#!/usr/bin/env bash

# This script file is used to test the consistency of files saved
# with sexpr python file. Spaces and line positioning will be ignored

if [[ $# < 1 ]]; then
    echo "Usage: $0 sexpr_files"
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

function test_sexpr {
    filename=`basename "$1"`

# python code --- START
python << EOF
import sexpr, re

# read file
f = open('$1')
data = ''.join(f.readlines())
out = sexpr.build_sexp(sexpr.parse_sexp(data))

# write file
f = open('/tmp/$filename.out', 'w')
f.write(out)
f.close()
EOF
# python code --- END

    orig="/tmp/$filename.orig"
    out="/tmp/$filename.out"

    cp "$1" "$orig"

    # format files before compare
    format_file "$orig"
    format_file "$out"

    # non matching files will remain in tmp directory
    [[ `diff -b "$orig" "$out"` ]] && return 0

    # remove the matching files
    rm -f "$orig" "$out"
    return 1
}

# colors
RED="\e[0;31m"
GREEN="\e[0;32m"
NOCOLOR="\e[0m"

for file in "$@"; do
    echo "* testing $file"
    if ( test_sexpr "$file" ); then
        echo -e "${RED}sexpr has generated a non identical output for the file: $file${NOCOLOR}"
    else
        echo -e "${GREEN}...OK${NOCOLOR}"
    fi
done
