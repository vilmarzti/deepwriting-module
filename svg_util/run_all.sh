tsc
FILE=../data/abc_svg/*.svg
for file in $FILE
do
    node ./build/flatten.js $file >> test.txt
done