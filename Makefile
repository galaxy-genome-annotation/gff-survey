GFFS := $(wildcard random-gff3s-from-helena/*)

stats.md: parse.py $(GFFS)
	python parse.py > stats.md
