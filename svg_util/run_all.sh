tsc
FILE=../data/gesten_svg/*.svg
for file in $FILE
do
    filename=$(basename -- "$file")
    echo "$filename" >> test.txt
    node ./build/flatten.js $file >> test.txt
done