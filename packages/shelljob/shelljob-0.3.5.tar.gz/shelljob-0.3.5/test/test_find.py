from shelljob import fs

files = fs.find( '/usr/local', name_regex = '.*\\.so' )
print( "\n".join(files) )
