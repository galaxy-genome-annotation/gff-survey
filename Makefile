GFFS := $(wildcard random-gff3s-from-helena/* */*.gff */*.gff3)

stats.md: parse-headers.py $(GFFS)
	python parse-headers.py > stats.md
