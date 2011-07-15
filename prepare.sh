#!/bin/bash

set -e

mkdir -p deps
PYTHON="$(which python2.6)"
CWD="$(pwd)"


if [ -f deps/python.egg ]; then
    rm deps/python.egg
fi

# Check if all the res/raw scripts don't have sintaxis errors
echo "Compiling res/raw"
pushd res/raw
python -m compileall . . > /dev/null
find . -iname \*.pyc -type f -delete
popd

# Build egg file from extra things
pushd python
echo "Compiling python scripts"
bash compress.sh
popd

rm -rf res/raw/filelist.txt
touch res/raw/filelist.txt

rm -rf libs/armeabi/lib_airi_*.so
COUNT=0
for i in $(ls deps); do
    cp deps/$i libs/armeabi/lib_airi_$COUNT.so
    echo "lib_airi_$COUNT.so $i" >> res/raw/filelist.txt
    ((COUNT = COUNT + 1 ))
done
