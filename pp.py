#!/usr/bin/python

import pprint, sys

file_name = sys.argv[1]
fp = open(file_name)
contents = fp.read()
pp = pprint.PrettyPrinter(indent=4)
data = eval(contents)
pp.pprint(data)
