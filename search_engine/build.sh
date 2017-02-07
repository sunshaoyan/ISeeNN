#!/bin/bash
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../../ -DCMAKE_BUILD_TYPE=Release
make
make install
cd ..
# rm -rf build
