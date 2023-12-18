#!/usr/bin/env python
import gzip
import re
import sys
import glob
from ruby import List, String, Dict
from collections import Counter

headers = Counter()
headers_perfile = Counter()
ext = Counter()
file_count = 0

def stderr(*args):
    print(*args, file=sys.stderr)


for fn in glob.glob("**/*.gff3") + glob.glob("**/*.gff") + glob.glob("**/*.gff.gz"):
    if fn.endswith('gff3'):
        ext['gff3'] += 1
    else:
        ext['gff'] += 1

    file_count += 1

    if fn.endswith('gz'):
        with gzip.open(fn, 'rt') as handle:
            lines = List(handle.read(4096).split('\n'))
    else:
        with open(fn, 'r') as handle:
            lines = List(handle.read(4096).split('\n'))

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
print("## Extension")
print()
print("File Extension | Count")
print("---------- | ----- ")
for k, v in dict(ext).items():
    print(f"`{k}` | {v}")
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
feature_type_so = Counter()
score_range = Counter()
tags = Counter()
tags_perfile = Counter()
percent_encoding = Counter()
percent_fail = Counter()
percent_unencoded = Counter()
trailing_semicolon = Counter()

for fn in sorted(glob.glob("**/*.gff3")) + sorted(glob.glob("**/*.gff.gz")):
    file_count += 1
    if fn.endswith('gz'):
        handle = gzip.open(fn, 'rt')
    else:
        handle = open(fn, 'r')

    uniq_tools_this_file = []
    scores_this_file = List()

    for line in handle:
        if line.startswith('##'):
            continue
        elif line.count('\t') <= 5:
            continue

        parts = line.split('\t')
        tab_count[len(parts)] += 1

        feature_type[parts[2]] += 1
        if ':' in parts[2]:
            feature_type_so[parts[2]] += 1

        if len(parts) > 8:
            seen_tags = List()

            for encoded in re.findall('%[0-9a-fA-F][0-9a-fA-F]', parts[8]):
                percent_encoding[encoded] += 1
            for unencoded in re.findall('( |\t|\n|%[^A-Fa-f0-9][A-Fa-f0-9]|%[A-Fa-f0-9][^A-Fa-f0-9]|\r)', parts[8]):
                percent_unencoded[unencoded] += 1

            if len(parts[8]) > 1 and parts[8][-1] == ';':
                trailing_semicolon[fn] += 1
            for tag_pair in parts[8].split(';'):
                if tag_pair.strip() == '.':
                    tags['__.__'] += 1
                    seen_tags.append('__.__')
                    continue

                if len(tag_pair.strip()) == 0:
                    tags['EMPTY'] += 1
                    seen_tags.append('EMPTY')
                    continue

                if tag_pair.count('=') > 0:
                    k, v  = tag_pair.split('=', 1)
                else:
                    k = tag_pair + " (Invalid, missing =)"

                tags[k] += 1
                seen_tags.append(k)
            for tag in seen_tags.uniq:
                tags_perfile[tag] += 1


        if parts[1] not in uniq_tools_this_file:
            uniq_tools_this_file.append(parts[1])

        scores_this_file.append(parts[5])

    for un in uniq_tools_this_file:
        tools[un] += 1

    scores = scores_this_file.uniq.select(lambda x: x != '.').map(lambda x: float(x))
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
    else:
        score_range['Does Not Use Scores'] += 1

    handle.close()

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
for k, v in Dict(tools.most_common(20)).sorted(lambda x: -x[1]):
    print(f"`{k}` | {v}")

print()
print("## Feature Types")
print()
print("Feature | Count")
print("---------- | -----")
for k, v in Dict(feature_type).sorted(lambda x: -x[1]):
    print(f"`{k}` | {v}")
print()
print("Feature (Using SO term) | Count")
print("---------- | -----")
for k, v in Dict(feature_type_so).sorted(lambda x: -x[1]):
    print(f"`{k}` | {v}")

print()
print("## Scores?")
print()
print("Score Range | Count")
print("---------- | -----")
for k, v in Dict(score_range).sorted(lambda x: -x[1]):
    print(f"`{k}` | {v}")

print()
print("## Tags")
print()
print("Tag        | Value | Percentage Using at least Once")
print("---------- | ----- | ------------------------------")
for k, v in Dict(tags.most_common(20)).sorted(lambda x: -x[1]):
    print(f"`{k}` | {v} | {100 * tags_perfile[k] / file_count:0.2f}%")

print()
print("## Percent Encoding")
print()
print("Tag        | Value | Count")
print("---------- | ----- | -----")
from urllib.parse import unquote
for k, v in percent_encoding.most_common(20):
    # percent unencode the key
    q = unquote(k)
    print(f"{k} | `{q}` | {v}")


print()
print("## Non-percent encoded values")
print()
print("Tag        | Count")
print("---------- | -----")
for k, v in percent_unencoded.most_common(20):
    print(f"`{k}` | {v}")


print()
print("## Trailing Semicolon in field 9")
print()
print("Tag        | Count")
print("---------- | -----")
for k, v in trailing_semicolon.most_common(20):
    print(f"`{k}` | {v}")
