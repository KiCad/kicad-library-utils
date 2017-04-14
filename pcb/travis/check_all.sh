SCRIPT="/home/travis/build/kicad-library-utils/pcb/check_kicad_mod.py"

error=0
for change in $(git diff --name-only --diff-filter=AM $TRAVIS_COMMIT_RANGE); do
    echo "Checking: $change"
    python3 $SCRIPT "/$1/$change" -vv
    error="$(($error+$?))"
done
exit $error
