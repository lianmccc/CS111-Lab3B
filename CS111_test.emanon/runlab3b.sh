#!/bin/bash

if [ $# -ne 1 ]
then
	echo 'Bad arguments'
	exit 1
fi

python lab3b.py $1 
