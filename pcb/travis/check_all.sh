SCRIPT="/home/travis/build/kicad-library-utils/pcb/check_kicad_mod.py"

echo "Commit range checked: $TRAVIS_COMMIT_RANGE"
test_two_dots=${TRAVIS_COMMIT_RANGE/.../..}
echo "$test_two_dots"
git --version
git diff --name-only --diff-filter=AMR $test_two_dots

error=0
for change in $(git diff --name-only --diff-filter=AMR $TRAVIS_COMMIT_RANGE); do
    echo "Checking: $change"
    python3 $SCRIPT "/$1/$change" -vv
    error="$(($error+$?))"
done
exit $error
