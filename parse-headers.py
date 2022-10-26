#!/usr/bin/env python
import sys
import glob
from ruby import List, String, Dict
from collections import Counter

headers = Counter()
headers_perfile = Counter()
file_count = 0

def stderr(*args):
    print(*args, file=sys.stderr)


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

    for line in cleaned_headers.uniq:
        headers_perfile[line] += 1


print("# Statistics")
print()
print("## Headers")
print()
print("Header Key | Value | Percentage Using at least Once")
print("---------- | ----- | -----------")
for k, v in sorted(dict(headers).items(), key=lambda x: x[0]):
    print(f"`{k}` | {v} | {100 * headers_perfile[k] / file_count:0.2f}%")

tab_count = Counter()
tools = Counter()
feature_type = Counter()
score_range = Counter()

for fn in sorted(glob.glob("**/*.gff3")):
    file_count += 1
    with open(fn, 'r') as handle:
        lines = List(handle.readlines())
        feature_lines = lines.strip.select(lambda x: not x.startswith('##')) \
            .select(lambda x: x.count('\t') > 5) \
            .map(lambda x: List(x.split('\t')))

        for parts in feature_lines:
            # if line.count('\t') != 8:
                # print(line)
            tab_count[parts.length] += 1

            tools[parts[1]] += 1
            feature_type[parts[2]] += 1

        uniq_tools = feature_lines.map(lambda x: x[1]).uniq

        scores = feature_lines.map(lambda x: x[5]).uniq.select(lambda x: x != '.').map(lambda x: float(x))
        if scores.length > 0:
            sus_min = min(scores)
            sus_max = max(scores)

            if 0 <= sus_min <= sus_max <= 100:
                score_range['[0, 100]'] +=1
            elif 0 <= sus_min <= sus_max <= 1000:
                score_range['[0, 1000]'] +=1
            elif 0 <= sus_min <= sus_max <= 10000:
                score_range['[0, 10000]'] +=1
            else:
                # very sus.
                score_range[f'[{sus_min}, {sus_max}]'] +=1
                # stderr(sus_min, sus_max)




print()
print("## Tabs")
print()
print("Tabs In Line | Count")
print("---------- | -----")
for k, v in dict(tab_count).items():
    print(f"`{k}` | {v}")


print()
print("## Tools")
print()
print("Tools | Count")
print("---------- | -----")
for k, v in Dict(tools).sorted(lambda x: -x[1]):
    print(f"`{k}` | {v}")

print()
print("## Feature Types")
print()
print("Feature | Count")
print("---------- | -----")
for k, v in Dict(feature_type).sorted(lambda x: -x[1]):
    print(f"`{k}` | {v}")

print()
print("## Scores?")
print()
print("Score Range | Count")
print("---------- | -----")
for k, v in Dict(score_range).sorted(lambda x: -x[1]):
    print(f"`{k}` | {v}")
