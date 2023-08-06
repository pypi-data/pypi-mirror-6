#!/bin/bash
#Join all results file in result directory and content is written to stdout

#Arguments:			first		result directory

sufix=".result"

echo "`ls $1 | head -n 1 | xargs head -n 1`"
for file in "$1"/*$sufix; do
	echo "`tail -n 1 $file`"
done
