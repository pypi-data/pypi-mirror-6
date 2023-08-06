def iscomment(s):
	return s.startwith('#')

with open(filename,'r') as f:
	for line in (x for x in f if not x.startswith('#')):
		print(line)