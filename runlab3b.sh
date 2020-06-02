#NAME: Mingchao Lian, Seoyoon Jin
#EMAIL: lianmccc@ucla.edu, seoyoonjin@g.ucla.edu
#ID: 005348062, 505297593

if [ $# -ne 1 ]
then
	echo 'Bad arguments'
	exit 1
fi

python lab3b.py $1 
