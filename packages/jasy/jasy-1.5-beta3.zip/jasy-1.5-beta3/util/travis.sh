#!/bin/bash

echo ">>> PREPARING ENVIRONMENT..."
cd bin || exit 1
if ! [ `which python3` ]; then
  ln -sf `which python` python3 || exit 1 
fi
export PATH="`pwd`:$PATH"; 
cd .. || exit 1

echo
echo ">>> RUNNING UNIT TESTS..."
jasy-test || exit 1

echo
echo ">>> RUNNING DOC GENERATOR..."
jasy-doc || exit 1

echo
echo ">>> EXECUTING JASY VERSION..."
jasy --version || exit 1

echo
echo ">>> EXECUTING JASY ABOUT..."
jasy about || exit 1

echo
echo ">>> EXECUTING JASY DOCTOR..."
jasy doctor || exit 1

echo
echo ">>> RUNNING JASY CREATE"
jasy create --name mytest --origin https://github.com/sebastian-software/core.git || exit 1

echo
echo ">>> EXECUTING HELP..."
cd mytest || exit 1
jasy help || exit 1
cd .. || exit1
rm -rf mytest || exit1

echo 
echo ">>> DONE - ALL FINE"
