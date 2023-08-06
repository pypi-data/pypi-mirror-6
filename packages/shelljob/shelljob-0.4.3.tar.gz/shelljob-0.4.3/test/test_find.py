from shelljob import fs

files = fs.find( '/usr/local', name_regex = '.*\\.so' )
print( "\n".join( iter(files) ) )
print( " - - ")

files = fs.find( '/usr/local', name_regex = '.*\\.so', relative = True )
print( "\n".join( iter(files) ) )
print( " - - ")

