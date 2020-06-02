#NAME: Mingchao Lian, Seoyoon Jin
#EMAIL: lianmccc@ucla.edu, seoyoonjin@g.ucla.edu
#ID: 005348062, 505297593

default: runlab3b.sh lab3b.py
	ln runlab3b.sh lab3b
	chmod u+x lab3b

clean:
	rm -f lab3b-005348062.tar.gz lab3b

dist:
	tar -czvf lab3b-005348062.tar.gz lab3b.py runlab3b.sh README Makefile