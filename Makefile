.PHONY: help system_requirements build debug clean open

help:
	@echo "Build:"
	@echo "  - build: Build a fresh copy of the thesis in the build/ folder."
	@echo "  - debug: Same as 'build', but pauses build on errors for easier debugging."
	@echo "  - clean: Clean working TeX build artifacts."
	@echo "  - open : Open up the current thesis PDF."
	@echo ""
	@echo "Supplementary Information:"
	@echo "  - help               : View this help guide."
	@echo "  - system_requirements: List system requirements."

system_requirements:
	@echo "System Requirements: LaTeX (latexmk + LuaLaTeX), Pygments, InkScape"
	@echo "  - working LaTeX installation (with latexmk and LuaLaTeX)"
	@echo "  - Pygments (for code snippet syntax highlighting, installed with Python/pip)"
	@echo "  - InkScape (for SVG-based figures)"

build: # standard build -- '-output-directory=build' is a special name and is referenced from '\usepackage{minted}'region in 'thesis.tex'
	latexmk -output-directory=build -pdflatex=lualatex -pdf -interaction=nonstopmode thesis.tex --shell-escape
	cp build/thesis.pdf thesis.pdf

debug: # for finding hard issues, this is an interactive version of 'build'
	latexmk -output-directory=build -pdflatex=lualatex -pdf thesis.tex --shell-escape

clean:
	rm -rf build/

open:
	xdg-open build/thesis.pdf
