SCRIPT="/home/travis/build/kicad-library-utils/pcb/check_kicad_mod.py"

error=0
# If IFS is left default (space) then any files with spaces will break the script
IFS=$"\n"
for change in $(git diff --name-only --diff-filter=AM $TRAVIS_COMMIT_RANGE); do
    echo "$change"
    python3 $SCRIPT "$change" -vv
    error="$(($error+$?))"
done
unset IFS
exit $error
