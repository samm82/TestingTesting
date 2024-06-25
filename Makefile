.PHONY: help system_requirements build debug clean open

STUBS = Supp Quality Approach
GLOSSARIES = $(addsuffix Glossary, $(STUBS))
CSV_GLOSSARIES = $(addsuffix .csv, $(GLOSSARIES))
TXT_GLOSSARIES = $(addsuffix .txt, $(GLOSSARIES))
DIFF_GLOSSARIES = $(addprefix Diff, $(TXT_GLOSSARIES))

help:
	@echo "Build:"
	@echo "  - build : Build a fresh copy of the thesis."
	@echo "  - notes : Build a fresh copy of just the notes section."
	@echo "  - debug : Same as 'build', but pauses build on errors for easier debugging."
	@echo "  - poster: Build a fresh copy of the testing terminology poster."
	@echo "  - clean : Clean working TeX build artifacts."
	@echo "  - open  : Open up the current thesis PDF."
	@echo ""
	@echo "Supplementary Information:"
	@echo "  - help               : View this help guide."
	@echo "  - system_requirements: List system requirements."
	@echo "  - gloss              : Open all relevant glossaries in Excel."
	@echo "  - csv_diff           : View changes to glossaries in an intuitive format."

system_requirements:
	@echo "System Requirements: LaTeX (latexmk + LuaLaTeX), Pygments, InkScape"
	@echo "  - working LaTeX installation (with latexmk and LuaLaTeX)"
	@echo "  - Pygments (for code snippet syntax highlighting, installed with Python/pip)"
	@echo "  - InkScape (for SVG-based figures)"

gloss:
	$(foreach gloss, $(CSV_GLOSSARIES),EXCEL.EXE $(gloss) &)

csv_diff:
	for gloss in $(GLOSSARIES) ; do \
		py scripts/diffCSV.py $$gloss; \
	done
	for gloss in $(DIFF_GLOSSARIES) ; do \
		git diff --word-diff=color --no-index --word-diff-regex=. scripts/$$gloss $$gloss; \
		if [ $$? -ne 1 ]; then echo "No diff in $$gloss"; rm $$gloss; fi; \
	done

build: notes # standard build -- '-output-directory=build' is a special name and is referenced from '\usepackage{minted}'region in 'thesis.tex'
# Attempted to convert the following find and replace working in VS Code:
# ([^p])p.[\s~]+(\d+)([-,])(\d+) -> $1pp.~$2$3$4
# To a Makefile rule unsuccessfully (grep not finding tildes):
# grep -Irwl "([^p])p.[\s~]+(\d+)([-,])(\d+)" --include='*.tex' . | xargs sed -ri "s/([^p])p.[\s~]+(\d+)([-,])(\d+)/\1pp.~\2\3\4/g"
	-latexmk -output-directory=build -pdflatex=lualatex -pdf -interaction=nonstopmode thesis.tex --shell-escape
	cp build/thesis.pdf thesis.pdf
# Update diff files for better diffs, ignore errors if no difference
	for gloss in $(DIFF_GLOSSARIES) ; do \
		if [ -f $$gloss ]; then mv $$gloss scripts/$$gloss; fi; \
	done

notes: # standard build of just notes -- '-output-directory=build' is a special name and is referenced from '\usepackage{minted}'region in 'thesis.tex'
# Attempted to convert the following find and replace working in VS Code:
# ([^p])p.[\s~]+(\d+)([-,])(\d+) -> $1pp.~$2$3$4
# To a Makefile rule unsuccessfully (grep not finding tildes):
# grep -Irwl "([^p])p.[\s~]+(\d+)([-,])(\d+)" --include='*.tex' . | xargs sed -ri "s/([^p])p.[\s~]+(\d+)([-,])(\d+)/\1pp.~\2\3\4/g"
	-latexmk -output-directory=build -pdflatex=lualatex -pdf -interaction=nonstopmode notes.tex --shell-escape
	cp build/notes.pdf notes.pdf

debug: # for finding hard issues, this is an interactive version of 'build'
	latexmk -output-directory=build -pdflatex=lualatex -pdf thesis.tex --shell-escape

poster:
	-latexmk -output-directory=build -pdflatex=lualatex -pdf -interaction=nonstopmode poster.tex --shell-escape
	cp build/poster.pdf poster.pdf

clean:
	rm -rf build/

open:
	xdg-open build/thesis.pdf
