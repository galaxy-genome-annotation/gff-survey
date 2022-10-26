GFFS := $(wildcard random-gff3s-from-helena/*)

stats.md: parse-headers.py $(GFFS)
	python parse-headers.py > stats.md
