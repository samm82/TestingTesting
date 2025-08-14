import re

from aenum import AutoNumberEnum, Enum, OrderedEnum
from collections import OrderedDict
from functools import reduce, total_ordering
import itertools
import operator

from helpers import *

class Color(OrderedEnum):
    GREEN  = 3
    BLUE   = 2
    MAROON = 1
    BLACK  = 0
    GREY   = -1
    ORANGE = -2

    def __str__(self):
        return self.name.lower()

@total_ordering
class SrcCat(AutoNumberEnum):

    class LabelType(Enum):
        FROM   = auto()
        SINGLE = auto()

    STD    = "Established Standards", "Standards", Color.GREEN, LabelType.FROM
    META   = "Terminology Collections", "Collections", Color.BLUE, LabelType.FROM
    TEXT   = "Textbooks", "Textbooks", Color.MAROON, LabelType.FROM
    PAPER  = "Papers and Other Documents", "Papers", Color.BLACK, LabelType.FROM
    INFER  = "Inferences", "Inferences", Color.GREY, LabelType.SINGLE
    PROP   = "Proposals", "Proposals", Color.ORANGE, LabelType.SINGLE

    def __init__(self, longname, shortname, color, labelType):
        self.longname  = longname
        self.shortname = shortname
        self.color     = color

        # Label for use in legends
        self.label = longname
        # From https://stackoverflow.com/a/4664889/10002168
        srcCatSpaces = [m.start() for m in re.finditer(" ", self.label)]
        if srcCatSpaces:
            # From comment on https://stackoverflow.com/a/38131003/10002168
            _idx = srcCatSpaces[len(srcCatSpaces)//2]
            # From https://stackoverflow.com/a/41753038/10002168
            self.label = self.label[:_idx] + "<br/>" + self.label[_idx + 1:]

        if labelType == self.LabelType.FROM:
            self.label = f"From {self.label}"
        elif labelType == self.LabelType.SINGLE:
            self.label = self.label[:-1]
        else:
            raise NotImplementedError("Unknown value of LabelType")

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.color < other.color
        return NotImplemented

# rel == True if the SrcCat is used for coloring relations
def getSrcCat(s, rel: bool = False) -> SrcCat:
    if "(infer" in s:
        return SrcCat.INFER
    # "StdAuthor" used for example
    if any(std in s for std in {"IEEE", "ISO", "IEC", "StdAuthor"}):
        return SrcCat.STD
    if any(metastd in s for metastd in
        {"Washizaki", "Bourque and Fairley", "SWEBOK",
            "Hamburg and Mogyorodi", "ISTQB", "Firesmith",
            "Doğan et al", "DoğanEtAl"}):
        return SrcCat.META
    if any(textbook in s for textbook in
        {"van Vliet", "vanVliet", "Patton", "Peters and Pedrycz",
            "PetersAndPedrycz", "Gerrard and Thompson",
            "GerrardAndThompson", "Dennis et al", "DennisEtAl",
            "Perry", "Ammann and Offutt", "AmmannAndOffutt",
            "Fenton and Pfleeger", "FentonAndPfleeger",
            "Kaner et al", "KanerEtAl"}):
        return SrcCat.TEXT
    return SrcCat.INFER if rel and not any(par in s for par in "()") else SrcCat.PAPER

def getExplicitness(explicitness: Explicitness | tuple[Explicitness]):
    if isinstance(explicitness, tuple):
        if any(e not in Explicitness for e in explicitness):
            raise ValueError(f"Invalid explicitness value in {explicitness}.")
        return Explicitness.IMP if Explicitness.IMP in explicitness else Explicitness.EXP
    return explicitness

def formatOutput(ls):
    return "%\n".join(map(str, ls))

class ExpImpCounter:
    def __init__(self):
        self.dict = {k: 0 for k in list(Explicitness)}
    
    def __str__(self):
        return str(tuple(self.dict.values()))

    def count(self):
        return sum(self.dict.values())

    def output(self):
        return formatOutput(self.dict.values())

    def addFlaw(self, explicitness: Explicitness | list[Explicitness]):
        self.dict[getExplicitness(explicitness)] += 1

class FlawCounter:
    def __init__(self, value):
        self.groundTruth, self.withinDoc, self.withinAuth = 0, 0, 0
        # Differences between two categories; may be within the same category
        self.betweenCats = {k : 0 for k in SrcCat if k.value <= value}
        self.flawDmns = OrderedDict({dc : ExpImpCounter() for dc in FlawDmn})
        self.flawMnfsts = OrderedDict({dc : ExpImpCounter() for dc in FlawMnfst})

    def __str__(self):
        return "\n".join(filter(None, [
            ", ".join(map(str, [self.groundTruth, self.withinDoc, self.withinAuth])),
            "Diffs: " + ", ".join([f"{k.name} {v}" for k, v in self.betweenCats.items()]),
            " | ".join(map(str, self.flawDmns.values())),
            " | ".join(map(str, self.flawMnfsts.values())),
            ])) + "\n"

    def _countHelper(d: dict) -> str:
        return formatOutput([v.output() for v in d.values()] +
                            [sum(v.count() for v in d.values())])

    def getCatCounts(self):
        return FlawCounter._countHelper(self.flawDmns)

    def getClsCounts(self):
        return FlawCounter._countHelper(self.flawMnfsts)

class FlawDmn(Enum):
    CATS   = "Categories"
    SYNS   = "Synonyms"
    PARS   = "Parents"
    DEFS   = "Definitions"
    LABELS = "Labels"
    SCOPE  = "Scope"
    TRACE  = "Traceability"

class FlawMnfst(Enum):
    WRONG  = "Mistakes"
    MISS   = "Omissions"
    CONTRA = "Contradictions"
    AMBI   = "Ambiguities"
    OVER   = "Overlaps"
    REDUN  = "Redundancies"

def sing(s: str) -> str:
    if s.endswith("ies"):
        return s[:-3] + "y"
    else:
        return s[:-1] if s.endswith("s") else s

def genFlawMacros(flawView):
    def formatMacro(k: FlawDmn | FlawMnfst, args: list[str] = ["s"],
                    extra: str = "") -> str:
        return (f"\\{"Renew" if k.name == "OVER" else "New"}DocumentCommand"
                f"{{\\{k.name.lower()}}}{{{" ".join(args)}}}"
                f"{{\\hyperref[{k.name.lower()}]"
                f"{{\\IfBooleanTF{{#1}}{{{sing(k.value)}}}{{{k.value}}}}}{extra}}}")

    writeFile([formatMacro(k) for k in flawView], f"{flawView.__name__}Macros", True)

COMPLEX_TEX_FILES = [
    "build/multiCats.tex",
    "build/multiSyns.tex",
    "build/parSyns.tex",
    "build/selfPars.tex",
    "chapters/05_flaws.tex",
]

SIMPLE_TEX_FILES = [
    "chapters/05a_main_flaws.tex",
    "chapters/05b_extra_flaws.tex",
]

TEX_FILES = COMPLEX_TEX_FILES + SIMPLE_TEX_FILES

simpleFlawMnfst = OrderedDict([
    # Based on https://tex.stackexchange.com/a/156061/192195
    #      and https://tex.stackexchange.com/a/338027/192195
    (k, ["\\ifnotpaper",
         f"\\begin{{enumerate}}[ref={sing(k.value)}~\\arabic*]",
         "\\else", f"\\begin{{itemize}}", "\\fi"])
         for k in FlawMnfst])

def outputFlaws():
    flawDict = {k : FlawCounter(k.value) for k in SrcCat if k.color.value >= 0}

    def printFlaws():
        print("\n".join(f"{k.name}: {v}" for k, v in flawDict.items()))
        print()

    def getFlawGroups(s):
        flawMnfst, flawDmn = re.search(
            r"% Flaw count \(([A-Z]+), ([A-Z]+)\):", s).groups()
        return FlawMnfst[flawMnfst], FlawDmn[flawDmn]

    for filename in TEX_FILES:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.readlines()
        flawCounts = [line for line in content if "% Flaw count" in line]
        # Don't process content before the first \item or after final \end{enumerate}
        flaws = [f"\\item % Flaw count {item}"
                    for item in "".join(content).rsplit(
                        "\\end{enumerate}", 1)[0].split(
                            "\\item % Flaw count ")[1:]]

        if "extra" in filename:
            for mnfstKey in simpleFlawMnfst.keys():
                simpleFlawMnfst[mnfstKey].append("\\ifnotpaper")

        if filename in SIMPLE_TEX_FILES:
            for flaw in flaws:
                flawMnfst, flawDmn = getFlawGroups(flaw)
                simpleFlawMnfst[flawMnfst].append(flaw)

                labels = re.findall(r"% Label ([a-z\-]+)", flaw)
                for label in labels:
                    simpleFlawMnfst[flawMnfst] = [re.sub(
                        r"\s+% Label [a-z\-]+\s+",
                        "\n          ".join(
                            ["", "\\\\phantomsection{}", f"\\\\label{{{label}}}", ""]),
                        line) for line in simpleFlawMnfst[flawMnfst]]
            
        if "extra" in filename:
            for mnfstKey in simpleFlawMnfst.keys():
                simpleFlawMnfst[mnfstKey].append("\\fi")

        for flaw in flawCounts:
            sources = flaw.split("|")
            flawMnfst, flawDmn = getFlawGroups(flaw)
            DEBUG = False

            sourceDicts = [categorizeSources(s) for s in sources]
            if DEBUG:
                print(sourceDicts, flawMnfst.name, flawDmn.name)

            def inPairs(s, *, sFunc = None):
                if sFunc:
                    s = [{sFunc(x) for x in si} for si in s]
                return set.union(*(a & b for a, b in itertools.combinations(s, 2)))

            # These ensure that sources aren't double counted
            # Note that pieAdded is used based on the previous presentation of flaws by source tier
            # As of #138, this is now done as a table, but this naming convention is still used
            pieAdded, tableAdded = set(), set()
            def updateCounters(source, pieSec: str, e):
                nonlocal flawDmn, flawMnfst

                if type(source) is tuple:
                    srcTuple = tuple(map(getSrcCat, source))
                    source = " ".join(map(lambda x: x.name.capitalize(), srcTuple))
                else:
                    srcTuple = tuple(map(getSrcCat, [source] * 2))
                sourceCat = srcTuple[0]

                # Don't bother counting flaws for examples
                if "Author" in source:
                    return

                if DEBUG:
                    print(source, sourceCat, pieSec, e)

                if srcTuple not in tableAdded:
                    if type(flawDict[sourceCat].flawDmns[flawDmn]) is int:
                        flawDict[sourceCat].flawDmns[flawDmn] += 1
                        flawDict[sourceCat].flawMnfsts[flawMnfst] += 1
                    else:
                        flawDict[sourceCat].flawDmns[flawDmn].addFlaw(e)
                        flawDict[sourceCat].flawMnfsts[flawMnfst].addFlaw(e)
                    tableAdded.add(srcTuple)
                if source not in pieAdded:
                    try:
                        getattr(flawDict[sourceCat], pieSec)[srcTuple[1]] += 1
                    except TypeError:
                        setattr(flawDict[sourceCat], pieSec,
                                getattr(flawDict[sourceCat], pieSec) + 1)
                    pieAdded.add(source)
                    if DEBUG:
                        print(f"{pieSec}:", source)
                    return True
                return False

            GROUP_SIZE = 2
            if len(sourceDicts) == 1:
                for e, sources in sourceDicts[0].items():
                    if sources and isinstance(e, Explicitness):
                        updateCounters(str(list(map("".join, sources))), "groundTruth", e)
            else:
                for dicts in itertools.combinations(sourceDicts, r=GROUP_SIZE):
                    for e in itertools.product(list(Explicitness), repeat=GROUP_SIZE):
                        try:
                            sets = [set(s[xi]) for s, xi in zip(dicts, e)]
                        except KeyError:
                            continue

                        for source in inPairs(sets, sFunc="".join):
                            updateCounters(source, "withinDoc", e)

                        for author in inPairs(sets, sFunc=lambda x: x[0]):
                            yearSets = [{y for a, y in s if a == author} for s in sets]
                            # Don't double count flaws within a single document
                            if (reduce(operator.mul, map(len, yearSets)) >
                                    len(inPairs(yearSets))):
                                updateCounters(author, "withinAuth", e)

                        for tup in {tuple(sorted([ai[0], bi[0]], key=getSrcCat))
                                for a, b in itertools.combinations(sets, 2)
                                for ai in a for bi in b if ai[0] != bi[0]}:
                            updateCounters(tup, "betweenCats", e)
            if DEBUG:
                printFlaws()

    for k in simpleFlawMnfst.keys():
        simpleFlawMnfst[k] += ["\\ifnotpaper", "\\end{enumerate}", "\\else",
                               "\\end{itemize}", "\\fi"]
        writeFile(simpleFlawMnfst[k], f"Flaw{"Mnfst"}{k.name.title()}", True)

    flawPies, flawBars, flawTable = [], [], []
    dmnTotal, mnfstTotal = [], []
    def totalHelper(total, new):
        return [a + b for a, b in itertools.zip_longest(
            total, [int(d.strip()) for d in new.split("%")], fillvalue=0)]

    for k, v in flawDict.items():
        flawDmns, flawMnfsts = v.getCatCounts(), v.getClsCounts()
        assert flawDmns.split("%")[-1] == flawMnfsts.split("%")[-1]

        dmnTotal   = totalHelper(dmnTotal,   flawDmns)
        mnfstTotal = totalHelper(mnfstTotal, flawMnfsts)

        writeFile([flawDmns],   f"{k.name.lower()}FlawDmnBrkdwn", True)
        writeFile([flawMnfsts], f"{k.name.lower()}FlawMnfstBrkdwn", True)

        totalFlaws = sum({v.groundTruth, v.withinDoc, v.withinAuth,
                             sum(v.betweenCats.values())})

        slices = ([(v.groundTruth, "With an assertion of ground truth"),
                   (v.withinDoc, "Within a single document"),
                   (v.withinAuth, "Between documents with the same set of authors")] +
                   [(catCount, "Between a document from this category and a " +
                     cat.shortname.lower()[:-1])  # Strip plural "s"
                     for cat, catCount in v.betweenCats.items()])

        # Default color palette for pgf-pie
        # https://github.com/pgf-tikz/pgf-pie/blob/ede5ceea348b0b1c1bbe8ccd0d75167ee3cc53bf/tex/latex/pgf-pie/tikzlibrarypie.code.tex#L239-L241
        DEFAULT_COLORS = ["blue!60", "cyan!60", "yellow!60", "orange!60", "red!60",
                          "blue!60!cyan!60", "cyan!60!yellow!60", "red!60!cyan!60",
                          "red!60!blue!60", "orange!60!cyan!60"]

        colors = [DEFAULT_COLORS[i] for i, slice in enumerate(slices) if slice[0]]

        # LaTeX from https://tex.stackexchange.com/a/196483/192195
        flawPies.append(["\\begin{subfigure}[t]{0.475\\textwidth}",
                          "\\begin{tikzpicture}[thick, scale=0.7, every label/.style={align=left, scale=0.7}]",
                          f"   \\pie[text=legend, sum=auto, hide number, color={{{", ".join(colors)}}}]{{",
                          ",\n".join(
                              [f"      {val}/{str(round(val/totalFlaws*100, 1)).strip("0").strip(".")}\\%"
                              for val, _ in slices if val]),
                          "}", "\\end{tikzpicture}",
                          f"\\caption{{Flaws found in \\{k.name.lower()}s{{}}.}}",
                          f"\\label{{fig:{k.name.lower()}FlawSources}}",
                          "\\end{subfigure}"
                          ])
        flawBars.append([val for val, _ in slices])
        flawTable.append([f"\\{k.name.lower()}s{{}}"] + [val for val, _ in slices])
    
    writeFile([formatOutput(dmnTotal)],   f"totalFlawDmnBrkdwn", True)
    writeFile([formatOutput(mnfstTotal)], f"totalFlawMnfstBrkdwn", True)

    flawLegend = ["\\begin{center}", "\\begin{subfigure}[t]{\\linewidth}",
                  "\\begin{tikzpicture}", "\\matrix [thick, draw=black] {",
                  "\\node[label=center:Legend] {{}}; \\\\",
                  *[f"\\node[thick, shape=rectangle, draw=black, fill={DEFAULT_COLORS[i]}, label=right:{{{slice[1]}}}]({i}) {{}}; \\\\"
                    for i, slice in enumerate(slices)], "};",
                  "\\end{tikzpicture}", "\\end{subfigure}", "\\end{center}"]
    flawPies.append(flawLegend)

    # From ChatGPT
    sepPieCharts: list[str] = []
    for i, item in enumerate(flawPies):
        sepPieCharts += item
        if i % 2:
            sepPieCharts.append("\\vskip\\baselineskip")
        else:
            sepPieCharts.append("\\hfill")

    FLAW_CAPTION = "Identified flaws by the \\hyperref[sources]{source tier} responsible."

    # writeFile(flawLegend, "flawLegend")
    # writeFile(["\\begin{figure*}", "\\centering"] + sepPieCharts +
    #             [f"\\caption{{{FLAW_CAPTION}}}",
    #             "\\label{fig:flawSources}", "\\end{figure*}"], "flawPies")

    flawCats = [cat.name.lower() for cat in SrcCat if cat.color.value >= 0]
    # Transpose 2D list; from https://stackoverflow.com/a/6473724/10002168
    flawBars = list(map(list, itertools.zip_longest(*flawBars, fillvalue=0)))

    # Filter out comparisons we don't make
    for i in range(3):
        flawBars[i-3] = flawBars[i-3][i+1:]
    FLAW_CAPTION += (" Some bars are omitted as they correspond to comparisons"
                     " we do not make; see \\Cref{flaw-cred-compare}.")

    flawBars = [f"\\addplot[fill={color}] coordinates {{{' '.join(
                reversed([str(x).replace("'", "") for x in zip(
                         reversed(flawCats), reversed(vals))]))}}};"
                    for color, vals in zip(DEFAULT_COLORS, flawBars)]
    writeFile(["\\begin{figure}[bt!]", "\\centering",
               "\\begin{tikzpicture}", "\\begin{axis}[",
                    "width=\\textwidth, height=9cm,",
                    # "x tick label style={rotate=90},",
                   f"symbolic x coords={{{",".join(flawCats)}}},",
                    "xtick=data,",  # "x tick label as interval,",
                   f"xticklabels={{{",".join(map(
                       lambda cat: f'{{\\parbox{{0.16\\textwidth}}{{\\centering \\{cat}s{{}}}}}}',
                       flawCats))}}},",
                    # "xlabel=Source Tier (see \\Cref{source-tiers}),",  # Legend should be -0.35 if xlabel
                    "ylabel=Flaws, ybar,",  # xbar=0pt, bar width=5, bar shift=3",
                    "enlargelimits=0.2, enlarge y limits=0.1,",
                    "legend style={at={(0.5,-0.25)}, anchor=north, legend columns=1,",
                    "inner xsep=6pt,inner ysep=4pt,",
                    "nodes={inner sep=4pt,text depth=0.3em},},",
                    "legend cell align=left,",
                    "nodes near coords,", # nodes near coords align={vertical}, point meta=y,"
                    "every node near coord/.append style={font=\\tiny},", "]",
               # Legend header from https://tex.stackexchange.com/a/2332/192195
            #    "\\addlegendimage{empty legend}",
               *flawBars,
            #    *map(lambda x: f"\\addlegendentry{{{x}}}",
            #         ["{\\centering \\textbf{Legend}}", *(vals[1] for vals in slices)]),
               f"\\legend{{{",".join([vals[1] for vals in slices])}}}",
               "\\end{axis}", "\\end{tikzpicture}", f"\\caption{{{FLAW_CAPTION}}}",
               "\\label{fig:flawBars}", "\\end{figure}"], "flawBars")

    # writeTblr("flawTable", FLAW_CAPTION,
    #               ["Flaw between a document \\\\ from a \\hyperref[sources]{source tier} \\\\ below and a(n) \\dots{}"] + [
    #                   f"\\rotatebox[origin=c]{{90}}{{\\parbox{{4.35cm}}{{\\centering {x}}}}}" 
    #                     for x in ["source of \\\\ ground truth",
    #                               "part of the same document",
    #                               "document with the same set of author(s)"] +
    #                              [cat.longname.lower()[:-1]  # Strip plural "s"
    #                               if cat.color != Color.BLACK else "paper or other document"
    #                                                   # Exclude inferences and proposals
    #                                 for cat in SrcCat if cat.color.value >= 0]],
    #               [" & ".join(map(str, x)) + " \\\\" for x in
    #                # From https://stackoverflow.com/a/63080837/10002168
    #                zip(*itertools.zip_longest(*flawTable, fillvalue="---"))],
    #                toSort=False, rowHeadSpec="r", rowDataSpec="c")
