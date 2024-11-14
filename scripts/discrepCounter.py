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
    GRAY   = -1

    def __str__(self):
        return self.name.lower()

@total_ordering
class SrcCat(AutoNumberEnum):
    STD    = "Established Standards", "Standards", Color.GREEN
    META   = "``Meta-level'' Collections", "``Meta-level'' Documents", Color.BLUE
    TEXT   = "Textbooks", "Textbooks", Color.MAROON
    PAPER  = "Papers and Other Documents", "Papers", Color.BLACK
    INFER  = "Inferences", "Inferences", Color.GRAY

    def __init__(self, longname, shortname, color):
        self.longname  = longname
        self.shortname = shortname
        self.color     = color

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.color < other.color
        return NotImplemented

# rel == True if the SrcCat is used for coloring relations
def getSrcCat(s, rel: bool = False) -> SrcCat:
    if any(std in s for std in {"IEEE", "ISO", "IEC"}):
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

def getRigidity(rigidity: Rigidity | tuple[Rigidity]):
    if isinstance(rigidity, tuple):
        if any(r not in Rigidity for r in rigidity):
            raise ValueError(f"Invalid rigidity value in {rigidity}.")
        return Rigidity.IMP if Rigidity.IMP in rigidity else Rigidity.EXP
    return rigidity

def formatOutput(ls):
    return "%\n".join(map(str, ls))

class ExpImpCounter:
    def __init__(self):
        self.dict = {k: 0 for k in list(Rigidity)}
    
    def __str__(self):
        return str(tuple(self.dict.values()))

    def count(self):
        return sum(self.dict.values())

    def output(self):
        return formatOutput(self.dict.values())

    def addDiscrep(self, rigidity: Rigidity | list[Rigidity]):
        self.dict[getRigidity(rigidity)] += 1

class DiscrepCounter:
    def __init__(self, value):
        self.withinDoc, self.withinAuth = 0, 0
        # Differences between two categories; may be within the same category
        self.betweenCats = {k : 0 for k in SrcCat if k.value <= value}
        self.discrepCats = OrderedDict({dc : ExpImpCounter() for dc in DiscrepCat})
        self.discrepClss = OrderedDict({dc : ExpImpCounter() for dc in DiscrepCls})

    def __str__(self):
        return "\n".join(filter(None, [
            ", ".join(map(str, [self.withinDoc, self.withinAuth])),
            "Diffs: " + ", ".join([f"{k.name} {v}" for k, v in self.betweenCats.items()]),
            " | ".join(map(str, self.discrepCats.values())),
            " | ".join(map(str, self.discrepClss.values())),
            ])) + "\n"

    def _countHelper(d: dict) -> str:
        return formatOutput([v.output() for v in d.values()] +
                            [sum(v.count() for v in d.values())])

    def getCatCounts(self):
        return DiscrepCounter._countHelper(self.discrepCats)

    def getClsCounts(self):
        return DiscrepCounter._countHelper(self.discrepClss)

class DiscrepCat(Enum):
    SYNS  = "Synonyms"
    PARS  = "Parents"
    CATS  = "Categories"
    DEFS  = "Definitions"
    TERMS = "Terminology"
    CITES = "Citations"

class DiscrepCls(Enum):
    WRONG  = "Mistakes"
    MISS   = "Omissions"
    CONTRA = "Contradictions"
    AMBI   = "Ambiguities"
    OVER   = "Overlaps"
    REDUN  = "Redunancies"

COMPLEX_TEX_FILES = [
    "build/multiSyns.tex",
    "build/parSyns.tex",
    "build/selfCycles.tex",
    "chapters/05_discrepancies.tex",
]

SIMPLE_TEX_FILES = [
    "chapters/05a_main_discreps.tex",
    "chapters/05b_extra_discreps.tex",
]

TEX_FILES = COMPLEX_TEX_FILES + SIMPLE_TEX_FILES

def enumOrItem(k):
    # Based on https://tex.stackexchange.com/a/156061/192195
    # and https://tex.stackexchange.com/a/338027/192195
    return (k, ["\\ifnotpaper", f"\\begin{{enumerate}}[ref={k.value}~Discrepancy~\\arabic*]",
                      "\\else", f"\\begin{{itemize}}", "\\fi"])
simpleDiscrepCats = OrderedDict([enumOrItem(k) for k in DiscrepCat])
simpleDiscrepClss = OrderedDict([enumOrItem(k) for k in DiscrepCls])

def outputDiscreps():
    discrepDict = {k : DiscrepCounter(k.value) for k in SrcCat if k.color.value >= 0}

    def printDiscreps():
        print("\n".join(f"{k.name}: {v}" for k, v in discrepDict.items()))
        print()

    def getDiscGroups(s):
        discCat, discCls = re.search(
            r"% Discrep count \(([A-Z]+), ([A-Z]+)\):", s).groups()
        return DiscrepCat[discCat], DiscrepCls[discCls]

    for filename in TEX_FILES:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.readlines()
        discrepCounts = [line for line in content if "% Discrep count" in line]
        # Don't process content before the first \item or after final \end{enumerate}
        discreps = [f"\\item % Discrep count {item}"
                    for item in "".join(content).rsplit(
                        "\\end{enumerate}", 1)[0].split(
                            "\\item % Discrep count ")[1:]]

        if "extra" in filename:
            for catKey in simpleDiscrepCats.keys():
                simpleDiscrepCats[catKey].append("\\ifnotpaper")
            for clsKey in simpleDiscrepClss.keys():
                simpleDiscrepClss[clsKey].append("\\ifnotpaper")

        if filename in SIMPLE_TEX_FILES:
            for discrep in discreps:
                discCat, discCls = getDiscGroups(discrep)
                simpleDiscrepCats[discCat].append(discrep)
                simpleDiscrepClss[discCls].append(discrep)
                try:
                    cat, label = re.search(
                        r"% Label ([A-Z]+) ([a-z\-]+)", discrep).groups()
                    for cls, dict in [(DiscrepCat, simpleDiscrepCats),
                                      (DiscrepCls, simpleDiscrepClss)]:
                        try:
                            dict[cls[cat]] = [re.sub(
                                r"% Label [A-Z]+ [a-z\-]+",
                                f"\\\\phantomsection{{}}\\\\label{{{label}-discrep}}",
                                line) for line in dict[cls[cat]]]
                        except KeyError:
                            continue
                except AttributeError:
                    continue
            
        if "extra" in filename:
            for catKey in simpleDiscrepCats.keys():
                simpleDiscrepCats[catKey].append("\\fi")
            for clsKey in simpleDiscrepClss.keys():
                simpleDiscrepClss[clsKey].append("\\fi")

        for discrep in discrepCounts:
            sources = discrep.split("|")
            discCat, discCls = getDiscGroups(discrep)
            DEBUG = False

            sourceDicts = [categorizeSources(s) for s in sources]
            if DEBUG:
                print(sourceDicts, discCat.name, discCls.name)

            def inPairs(s, *, sFunc = None):
                if sFunc:
                    s = [{sFunc(x) for x in si} for si in s]
                return set.union(*(a & b for a, b in itertools.combinations(s, 2)))

            # These ensure that sources aren't double counted
            pieAdded, tableAdded = set(), set()
            def updateCounters(source, pieSec: str, r):
                nonlocal discCat, discCls

                if type(source) is tuple:
                    srcTuple = tuple(map(getSrcCat, source))
                    source = " ".join(map(lambda x: x.name.capitalize(), srcTuple))
                else:
                    srcTuple = tuple(map(getSrcCat, [source] * 2))
                sourceCat = srcTuple[0]

                # Don't bother counting discrepancies for examples
                if "Author" in source:
                    return

                if DEBUG:
                    print(source, sourceCat, pieSec, r)

                if srcTuple not in tableAdded:
                    if type(discrepDict[sourceCat].discrepCats[discCat]) is int:
                        discrepDict[sourceCat].discrepCats[discCat] += 1
                        discrepDict[sourceCat].discrepClss[discCls] += 1
                    else:
                        discrepDict[sourceCat].discrepCats[discCat].addDiscrep(r)
                        discrepDict[sourceCat].discrepClss[discCls].addDiscrep(r)
                    tableAdded.add(srcTuple)
                if source not in pieAdded:
                    try:
                        getattr(discrepDict[sourceCat], pieSec)[srcTuple[1]] += 1
                    except TypeError:
                        setattr(discrepDict[sourceCat], pieSec,
                                getattr(discrepDict[sourceCat], pieSec) + 1)
                    pieAdded.add(source)
                    if DEBUG:
                        print(f"{pieSec}:", source)
                    return True
                return False

            GROUP_SIZE = 2
            if len(sourceDicts) == 1:
                for r, sources in sourceDicts[0].items():
                    if sources and isinstance(r, Rigidity):
                        updateCounters(str(list(map("".join, sources))), "withinDoc", r)
            else:
                for dicts in itertools.combinations(sourceDicts, r=GROUP_SIZE):
                    for r in itertools.product(list(Rigidity), repeat=GROUP_SIZE):
                        try:
                            sets = [set(s[xi]) for s, xi in zip(dicts, r)]
                        except KeyError:
                            continue

                        for source in inPairs(sets, sFunc="".join):
                            updateCounters(source, "withinDoc", r)

                        for author in inPairs(sets, sFunc=lambda x: x[0]):
                            yearSets = [{y for a, y in s if a == author} for s in sets]
                            # Don't double count discrepancies within a single document
                            if (reduce(operator.mul, map(len, yearSets)) >
                                    len(inPairs(yearSets))):
                                updateCounters(author, "withinAuth", r)

                        for tup in {tuple(sorted([ai[0], bi[0]], key=getSrcCat))
                                for a, b in itertools.combinations(sets, 2)
                                for ai in a for bi in b if ai[0] != bi[0]}:
                            updateCounters(tup, "betweenCats", r)
            if DEBUG:
                printDiscreps()

    for shortname, discrepGroup in [("Cat", simpleDiscrepCats),
                                    ("Cls", simpleDiscrepClss)]:
        for k in discrepGroup.keys():
            discrepGroup[k] += ["\\ifnotpaper", "\\end{enumerate}", "\\else",
                                "\\end{itemize}", "\\fi"]
            writeFile(discrepGroup[k], f"Discrep{shortname}{k.name.title()}", True)

    pieCharts = []
    totalCats, totalClss = [], []
    def totalHelper(total, new):
        return [a + b for a, b in itertools.zip_longest(
            total, [int(d.strip()) for d in new.split("%")], fillvalue=0)]

    for k, v in discrepDict.items():
        discrepCats, discrepClss = v.getCatCounts(), v.getClsCounts()
        assert discrepCats.split("%")[-1] == discrepClss.split("%")[-1]

        totalCats = totalHelper(totalCats, discrepCats)
        totalClss = totalHelper(totalClss, discrepClss)

        writeFile([discrepCats], f"{k.name.lower()}DiscCatBrkdwn", True)
        writeFile([discrepClss], f"{k.name.lower()}DiscClsBrkdwn", True)

        totalDiscreps = sum({v.withinDoc, v.withinAuth,
                                sum(v.betweenCats.values())})

        slices = ([(v.withinDoc, "Within a single document"),
                    (v.withinAuth, "Between documents by the same author(s) or standards organization(s)")] +
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
        pieCharts.append(["\\begin{subfigure}[t]{0.475\\textwidth}",
                            "\\begin{tikzpicture}[thick, scale=0.7, every label/.style={align=left, scale=0.7}]",
                            f"   \\pie[text=legend, sum=auto, hide number, color={{{", ".join(colors)}}}]{{",
                            ",\n".join(
                                [f"      {val}/{str(round(val/totalDiscreps*100, 1)).strip("0").strip(".")}\\%"
                                for val, _ in slices if val]),
                            "}", "\\end{tikzpicture}",
                            f"\\caption{{Discrepancies found in \\{k.name.lower()}s{{}}.}}",
                            f"\\label{{fig:{k.name.lower()}DiscrepSources}}",
                            "\\end{subfigure}"
                            ])
    
    writeFile([formatOutput(totalCats)], f"totalDiscCatBrkdwn", True)
    writeFile([formatOutput(totalClss)], f"totalDiscClsBrkdwn", True)

    pieCharts.append(["\\begin{center}", "\\begin{subfigure}[t]{\\linewidth}",
                        "\\begin{tikzpicture}", "\\matrix [thick, draw=black] {",
                        "\\node[label=center:Legend] {{}}; \\\\"] +
                        [f"\\node[thick, shape=rectangle, draw=black, fill={DEFAULT_COLORS[i]}, label=right:{{{slice[1]}}}]({i}) {{}}; \\\\"
                        for i, slice in enumerate(slices)] +
                        ["};", "\\end{tikzpicture}", "\\end{subfigure}", "\\end{center}"])

    # From ChatGPT
    sepPieCharts: list[str] = []
    for i, item in enumerate(pieCharts):
        sepPieCharts += item
        if i % 2:
            sepPieCharts.append("\\vskip\\baselineskip")
        else:
            sepPieCharts.append("\\hfill")

    writeFile(["\\begin{figure*}", "\\centering"] + sepPieCharts +
                ["\\caption{Sources of discrepancies based on \\hyperref[sources]{source category}.}",
                "\\label{fig:discrepSources}", "\\end{figure*}"], "pieCharts")
