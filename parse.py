#!/usr/bin/env python
import glob
from ruby import List, String
from collections import Counter

headers = Counter()

for fn in glob.glob("**/*.gff3"):
    with open(fn, 'r') as handle:
        lines = List(handle.readlines())

    for line in lines.strip.select(lambda x: x.startswith('##')):
        vals = String(line[2:])

        if vals.match('gff-version'):
            headers[vals] += 1
        elif len(vals) == 0:
            headers['EMPTY HEADER'] +=1
        else:
            valss = vals.split()
            headers[valss[0]] += 1


print("Header Key | Value")
print("---------- | -----")
for k, v in sorted(dict(headers).items(), key=lambda x: x[0]):
    print(f"`{k}` | {v}")
