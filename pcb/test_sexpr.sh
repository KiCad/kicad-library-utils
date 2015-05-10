#!/usr/bin/bash

# This script file is used to test the consistency of files saved
# with sexpr python file. Spaces and line positioning will be ignored

if [[ $# < 1 ]]; then
    echo "Usage: $0 sexpr_files"
    exit 1
fi

function test_sexpr {
    filename=`basename "$1"`

# python code --- START
python << EOF
import sexpr
f = open('$1')
data = ''.join(f.readlines())
out = sexpr.build_sexp(sexpr.parse_sexp(data))
f = open('/tmp/$filename.out', 'w')
f.write(out)
f.close()
EOF
# python code --- END

    # remove spaces and new lines, sort the file and re-add some new lines
    tr -d ' \n' < "$1" | sort | tr '(' '\n(' > "/tmp/$filename.original.sorted"
    tr -d ' \n' < "/tmp/$filename.out" | sort | tr '(' '\n(' > "/tmp/$filename.out.sorted"

    [[ `diff -b "/tmp/$filename.original.sorted" "/tmp/$filename.out.sorted"` ]] && return 0
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
