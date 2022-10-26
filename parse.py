#!/usr/bin/env python
import glob
from ruby import List, String
from collections import Counter

headers = Counter()
headers_perfile = Counter()
file_count = 0

for fn in glob.glob("**/*.gff3"):
    file_count += 1
    with open(fn, 'r') as handle:
        lines = List(handle.readlines())

    header_lines = lines.strip.select(lambda x: x.startswith('##'))

    def header_cleaner(line):
        vals = String(line[2:])

        if vals.match('gff-version'):
            return vals
        elif len(vals) == 0:
            return 'EMPTY HEADER'
        else:
            valss = vals.split()
            return valss[0]

    cleaned_headers = header_lines.map(header_cleaner)

    for line in cleaned_headers:
        headers[line] += 1

    for line in cleaned_headers.uniq():
        headers_perfile[line] += 1




print("Header Key | Value | Percentage Using at least Once")
print("---------- | ----- | -----------")
for k, v in sorted(dict(headers).items(), key=lambda x: x[0]):
    print(f"`{k}` | {v} | {100 * headers_perfile[k] / file_count:0.2f}%")
