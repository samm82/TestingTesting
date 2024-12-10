BEGIN = "\\begin{itemize}"
END = "\\end{itemize}"

indented = False

paperOut, notPaperOut = [], []

class UndefinedTerm:
    def __init__(self, name, sources, indent=False, footnote=""):
        self.name = name
        self.sources = sources
        self.indent = indent
        self.footnote = footnote

    def render(self):
        global indented
        if indented ^ self.indent:
            if self.indent:
                change = BEGIN
                indented = True
            else:
                change = END
                indented = False
            paperOut.append(change)
            notPaperOut.append(change)
        paperOut.append(f"\\item {self.name}")
        footnote = f"\\footnote{{{self.footnote}}}" if self.footnote else ""
        notPaperOut.append(
            f"\\item \\textbf{{{self.name}{footnote}:}} \\citet{{{self.sources}}}")

undefTerms = [
    UndefinedTerm("Assertion Checking",
                  "LahiriEtAl2013,ChalinEtAl2006,BerdineEtAl2006"),
    UndefinedTerm("Loop Testing", "DhokAndRamanathan2016,"
                  "GodefroidAndLuchaup2011,PreußeEtAl2012,ForsythEtAl2004",
                  footnote="\\ifnotpaper \\else References \\fi"
                  "\\citep{ISO2015} and \\citep{ISO2022} "
                  "were used as reference for terms but not fully "
                  "investigated, \\citep{TrudnowskiEtAl2017} and "
                  "\\citep{PierreEtAl2017} were added as potentially in "
                  "scope, and \\citep{Goralski1999} and "
                  "\\citep{Dominguez-PumarEtAl2020} were added as "
                  "out-of-scope examples."),
    UndefinedTerm("EMSEC Testing", "ZhouEtAl2012,ISO2021"),
    UndefinedTerm("Asynchronous Testing", "JardEtAl1999"),
    UndefinedTerm("Performance(-related) Testing", "Moghadam2019"),
    UndefinedTerm("Web Application Testing", "DoğanEtAl2014, Kam2008"),
    UndefinedTerm("HTML Testing",
                  "ChoudharyEtAl2010,SneedAndGöschl2000,Gerrard2000b",
                  indent=True),
    UndefinedTerm("\\acf{dom} Testing", "BajammalAndMesbah2018", indent=True),
    UndefinedTerm("Sandwich Testing", "SharmaEtAl2021,SangwanAndLaPlante2006"),
    UndefinedTerm("Orthogonal Array Testing", "Mandl1985,Valcheva2013",
                  footnote="\\ifnotpaper \\else References \\fi"
                  "\\citep{YuEtAl2011} and \\citep{Tsui2007} were added as "
                  "out-of-scope examples."),
    UndefinedTerm("Backup Testing", "Bas2024", footnote="See \\Cref{recov-discrep}."),
]

for term in undefTerms:
    term.render()

paperOut = [BEGIN] + paperOut + [END]
notPaperOut = [BEGIN] + notPaperOut + [END]

PAPER_SOURCES = True

with open(f"build/undefTerms.tex", "w+", encoding="utf-8") as outFile:
    if PAPER_SOURCES:
        outFile.writelines("\n".join(notPaperOut))
    else:
       outFile.writelines("\n".join(
            ["\\ifnotpaper"] + notPaperOut + ["\\else"] + paperOut + ["\\fi"]))
