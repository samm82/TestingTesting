# Putting Software Testing Terminology to the Test

Samuel Crawford's M.A.Sc. thesis on software testing terminology.

## Build

Before building, you will need to install:

- a working [LaTeX installation](https://github.com/JacquesCarette/Drasil/wiki/New-Workspace-Setup#LaTeX),
- [Pygments](https://pygments.org/), and
- [InkScape](https://inkscape.org/).

Please run `make system_requirements` for an up-to-date list of system
requirements for building this thesis. Everything related to building
the thesis is contained in the `Makefile`; example commands you may find
useful are:
- `make <X>`: will build the corresponding `X.pdf` where `X` is one of
  `thesis`, `paper`, `seminar`, and `defense`, among others.
- `make graphs`: will build all visualizations of test approach relations,
  including those created manually or used as examples. (Note that this will
  take a while, mainly due to the size of `approachGraph.pdf`.)
- `make docs`: equivalent to running `make paper thesis seminar defense`.

<!--
To build it, you can run `make
build` in your shell, and it will create a `build/` folder locally, containing
the desired final `thesis.pdf` file.

If you're building for printing, please edit the `compilingforprinting` option
in the `manifest.tex` configuration file and rebuild the document.
-->

### Configuration

Please view `manifest.tex` for information about configuring the build.

### Debugging

`make thesis` runs fast because it runs without interactivity. To run the TeX
build of this _thesis_ interactively, please run `make debug` instead of
`make thesis`. This will allow you to debug any visual artifacts found in
the PDF, or the lack thereof.

## Source Code Organization

Personally, I tend to prefer "just text" in my TeX files, importing cluttering
code (such as that in tables, figures, etc.) from external files. This helps me
quickly find and edit my assets. However, you should not restrict yourself to my
preferences. Please feel free to use my general schema, or not. In particular,
I've divided up my chapters into a separate file for each, my front matter into
separate files, and each of my "assets" into a separate folder and file as
required.

`thesis.tex` is the main TeX file, importing all other things. In particular, it
imports:
- metadata from `manifest.tex`,
- bib references from `references.bib`,
- external assets (such as images, figures, tables) from `assets.tex`,
- chapter information from `front.tex`, `chapters.tex`, and `back.tex`, all
  respectively for the front, main, and back matters,
- helpful macros you might build for yourself, or that I found particularly,
  useful when building my thesis, from `macros.tex`, and
- the McMaster University colour swatch from `mcmaster_colours.tex`.

You should be mindful of all of these above listed files. Each one will have its
own discussion of its usage in its respective header, but you are free to ignore
the general schema I've built, or to modify it to your liking.

## Credits and Acknowledgements

This thesis was based on Jason Balaci's [McMaster thesis template](https://github.com/balacij/McMaster-Thesis-Template)
which provided many provided many helper LaTeX functions; slides were also
_heavily_ based on a previous presentation of his. Christopher William
Schankula also helped me with LaTeX and multiple friends discussed software
testing with me, providing many of the approaches in Section 3.5. A special
"thank you" to Dr. Stuart Reid for providing me with a paper he wrote that I
could not find online, for his work with ISO, and for founding the International
Software Testing Qualifications Board (ISTQB)! My family has also supported me
in more ways than I can count, and I cannot thank them enough. Finally, Dr.
Spencer Smith and Dr. Jacques Carette have been great supervisors and valuable
sources of guidance and feedback.

ChatGPT was used to help generate supplementary Python code for constructing
visualizations and generating LaTeX code, including regex. ChatGPT and
GitHub Copilot were both used for assistance with LaTeX formatting. ChatGPT
and ProWritingAid were both used for proofreading. ChatGPT also provided
pointers to the potential existence of some of the approaches in Section 3.5.

### Thesis Template Credits

Jason Balaci built his [McMaster thesis template](https://github.com/balacij/McMaster-Thesis-Template) using
"publicly available resources, such as [Overleaf](https://www.overleaf.com/),
[LaTeX Wikibooks](https://en.wikibooks.org/wiki/LaTeX), as well as many works
by individuals (for both inspiration and code snippets), in no particular order:

- Benjamin Furman's [McMaster Thesis Example](https://www.overleaf.com/LaTeX/templates/mcmaster-thesis-example/bjccppctqwgt)
based on Steven Gunn and Sunil Patel's work.
- Geneva Smith's [McMaster thesis template](https://www.eng.mcmaster.ca/cas/current-graduates#Graduate-Student-Forms).
- Clemens Niederberger for this public [StackOverflow response](https://tex.stackexchange.com/a/257896).
- Arash Esbati for this public [StackOverflow response](https://tex.stackexchange.com/a/254177).
- Gabriel Devenyi's [McMaster Thesis
  LaTeX](https://github.com/gdevenyi/mcmaster.LaTeX), specifically for the
  bibliography code.
- 'tom' from
  [TeXBlog](https://texblog.org/2012/03/21/cross-referencing-list-items/)."
