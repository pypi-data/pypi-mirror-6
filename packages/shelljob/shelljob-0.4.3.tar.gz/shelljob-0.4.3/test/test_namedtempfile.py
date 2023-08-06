import os
from shelljob import fs, proc

with fs.NamedTempFile() as nm:
	name = nm
	f = open(nm,"w")
	f.write( "Hello" )
	f.close()
	print( nm )
	
	f = open(nm,"r")
	assert f.read() == "Hello"
	
assert not os.path.exists(name)

with fs.NamedTempFile( prefix = 'PRE', suffix = '.END' ) as nm:
	assert nm.find( 'PRE' ) > 0 # can't be first due to directory
	assert nm.endswith( '.END' )
	name = nm
assert not os.path.exists(name)

# ensure deleted on exception
try:
	with fs.NamedTempFile as nm:
		name = nm
		raise Exception("oops")
except Exception, e:
	assert not os.path.exists(name)

# Example from docs
with fs.NamedTempFile() as nm:
	proc.call( "curl http://mortoray.com/ -o {}".format( nm ) )
	html = open(nm,'r').read()
	print( len(html) )
	
	name = nm
assert not os.path.exists(name)
