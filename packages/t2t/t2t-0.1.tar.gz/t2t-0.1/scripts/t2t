#!/usr/bin/evn python

import sys
import json
import re

patterns = json.load(open(sys.argv[1]))

while 1:
  line = sys.stdin.readline()
  for src, dst in patterns.iteritems():
  	p = re.compile(src)
  	res = p.match(line)
  	if res:
  		for i in range(len(res.groups())):
  			val = res.groups()[i]
  			dst = dst.replace("$%d" % (i + 1), val)
 		print dst
  		continue