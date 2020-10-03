#!/bin/bash
npm run flatten
FILES=../data/abc_svg/*.svg
for file in $FILES
do
    node ./build/flatten.js $file >> test.txt

done
