#! /bin/bash

input=$1

echo stripping $input ...
output=`basename $input`
grep -v nan $input | awk '{ {printf "%s\t%s\t",$1,$5} ;  for(i=7;i<=NF;++i){printf "%s\t",$i} ; {printf "\n"} }' > $output
echo "stripped file in $output."
