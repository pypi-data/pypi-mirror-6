import sys

from shelljob import proc

sp = proc.Group()
sp.run( [ "bash", "-c", "for ((i=0;i<10;i=i+1)); do echo $i; sleep 1; done" ] )
while sp.is_pending():
	lines = sp.readlines()
	for proc, line in lines:
		sys.stdout.write( "{}:{}".format( proc.pid, line ) )
