MKHTML=mkdoc --target=html --stylesheet=single-file
MKHTML_OPT=--param toc.section.depth=1

SRC=.

TXTFILES:= $(wildcard *.txt)
TARGET := $(TXTFILES:.txt=.html)

all: ${TARGET}

%.html: %.txt
	${MKHTML} ${MKHTMLOPTS} $<

clean:
	rm -f *.html
