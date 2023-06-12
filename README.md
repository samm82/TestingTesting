# McMaster Thesis Template

A thesis template for McMaster students.

## System Requirements

You will need to install:

* a working [LaTeX installation](https://github.com/JacquesCarette/Drasil/wiki/New-Workspace-Setup#latex),
* [Pygments](https://pygments.org/), and
* [InkScape](https://inkscape.org/).

Please run `make system_requirements` for an up-to-date list of system
requirements for building the report.

## Build

Before building, please ensure that you have the related [system
requirements](#system-requirements) installed. Everything related to building
the thesis report is contained in the `Makefile`. To build it, you can run `make
build` in your shell, and it will create a `build/` folder locally, containing
the desired final `thesis.pdf` file.

If you're building for printing, please edit the `compilingforprinting` option
in the `manifest.tex` configuration file and rebuild the document.

### Debugging

`make build` runs fast because it runs without interactivity. To run the TeX
build interactively, please run `make debug` instead of `make build` when
building your thesis. This will allow you to debug any visual artifacts found in
your PDF, or the lack thereof.

## Configuration

Please view `manifest.tex` for information about configuring the build.

## Source Code Organization

Personally, I tend to prefer “just text” in my TeX files, importing cluttering
code (such as that in tables, figures, etc.) from external files. This helps me
quickly find and edit my assets. However, you should not restrict yourself to my
preferences. Please feel free to use my general schema, or not. In particular,
I've divided up my chapters into a separate file for each, my front matter into
separate files, and each of my “assets” into a separate folder and file as
required.

`thesis.tex` is the main TeX file, importing all other things. In particular, it
imports:
* metadata from `manifest.tex`,
* bib references from `references.bib`,
* external assets (such as images, figures, tables) from `assets.tex`,
* chapter information from `front.tex`, `chapters.tex`, and `back.tex`, all
  respectively for the front, main, and back matters,
* helpful macros you might build for yourself, or that I found particularly,
  useful when building my thesis, from `macros.tex`, and
* the McMaster University colour swatch from `mcmaster_colours.tex`.

You should be mindful of all of these above listed files. Each one will have its
own discussion of its usage in its respective header, but you are free to ignore
the general schema I've built, or to modify it to your liking.

## Credits

Please note that I built this template using publicly available resources, such
as [Overleaf](https://www.overleaf.com/), [LaTeX
Wikibooks](https://en.wikibooks.org/wiki/LaTeX), as well as many works by
individuals (for both inspiration and code snippets), in no particular order:

* Benjamin Furman's [McMaster Thesis Example](https://www.overleaf.com/latex/templates/mcmaster-thesis-example/bjccppctqwgt) based on Steven Gunn and Sunil Patel's work.
* Geneva Smith's [McMaster thesis template](https://www.eng.mcmaster.ca/cas/current-graduates#Graduate-Student-Forms).
* Clemens Niederberger for this public [StackOverflow response](https://tex.stackexchange.com/a/257896).
* Arash Esbati for this public [StackOverflow response](https://tex.stackexchange.com/a/254177).
* Gabriel Devenyi's [McMaster Thesis
  LaTeX](https://github.com/gdevenyi/mcmaster.latex), specifically for the
  bibliography code.
* "tom" from
  [TeXBlog](https://texblog.org/2012/03/21/cross-referencing-list-items/).

If you feel you should be added to this list, please feel free to open a ticket
or email me, and I will add you as soon as I can.
