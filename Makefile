#NAME: Mingchao Lian, Seoyoon Jin
#EMAIL: lianmccc@ucla.edu, seoyoonjin@g.ucla.edu
#ID: 005348062, 505297593

default: 
	chmod u+x lab3b

clean:
	rm -f lab3b-005348062.tar.gz

dist:
	tar -czvf lab3b-005348062.tar.gz lab3b.py README Makefile