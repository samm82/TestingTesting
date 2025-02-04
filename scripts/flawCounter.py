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

    def addFlaw(self, rigidity: Rigidity | list[Rigidity]):
        self.dict[getRigidity(rigidity)] += 1

class FlawCounter:
    def __init__(self, value):
        self.groundTruth, self.withinDoc, self.withinAuth = 0, 0, 0
        # Differences between two categories; may be within the same category
        self.betweenCats = {k : 0 for k in SrcCat if k.value <= value}
        self.smntcFlaws = OrderedDict({dc : ExpImpCounter() for dc in FlawSmntc})
        self.sntxFlaws = OrderedDict({dc : ExpImpCounter() for dc in FlawSntx})

    def __str__(self):
        return "\n".join(filter(None, [
            ", ".join(map(str, [self.groundTruth, self.withinDoc, self.withinAuth])),
            "Diffs: " + ", ".join([f"{k.name} {v}" for k, v in self.betweenCats.items()]),
            " | ".join(map(str, self.smntcFlaws.values())),
            " | ".join(map(str, self.sntxFlaws.values())),
            ])) + "\n"

    def _countHelper(d: dict) -> str:
        return formatOutput([v.output() for v in d.values()] +
                            [sum(v.count() for v in d.values())])

    def getCatCounts(self):
        return FlawCounter._countHelper(self.smntcFlaws)

    def getClsCounts(self):
        return FlawCounter._countHelper(self.sntxFlaws)

class FlawSmntc(Enum):
    CATS  = "Categories"
    SYNS  = "Synonyms"
    PARS  = "Parents"
    DEFS  = "Definitions"
    TERMS = "Terminology"
    CITES = "Citations"

class FlawSntx(Enum):
    WRONG  = "Mistakes"
    MISS   = "Omissions"
    CONTRA = "Contradictions"
    AMBI   = "Ambiguities"
    OVER   = "Overlaps"
    REDUN  = "Redunancies"

COMPLEX_TEX_FILES = [
    "build/multiCats.tex",
    "build/multiSyns.tex",
    "build/parSyns.tex",
    "build/selfCycles.tex",
    "chapters/05_flaws.tex",
]

SIMPLE_TEX_FILES = [
    "chapters/05a_main_flaws.tex",
    "chapters/05b_extra_flaws.tex",
]

TEX_FILES = COMPLEX_TEX_FILES + SIMPLE_TEX_FILES

def enumOrItem(k):
    # Based on https://tex.stackexchange.com/a/156061/192195
    # and https://tex.stackexchange.com/a/338027/192195
    return (k, ["\\ifnotpaper", f"\\begin{{enumerate}}[ref={k.value}~Flaw~\\arabic*]",
                      "\\else", f"\\begin{{itemize}}", "\\fi"])
simpleFlawSmntc = OrderedDict([enumOrItem(k) for k in FlawSmntc])
simpleFlawSntx  = OrderedDict([enumOrItem(k) for k in FlawSntx])

def outputFlaws():
    flawDict = {k : FlawCounter(k.value) for k in SrcCat if k.color.value >= 0}

    def printFlaws():
        print("\n".join(f"{k.name}: {v}" for k, v in flawDict.items()))
        print()

    def getFlawGroups(s):
        smntcFlaw, sntxFlaw = re.search(
            r"% Flaw count \(([A-Z]+), ([A-Z]+)\):", s).groups()
        return FlawSmntc[smntcFlaw], FlawSntx[sntxFlaw]

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
            for smntcKey in simpleFlawSmntc.keys():
                simpleFlawSmntc[smntcKey].append("\\ifnotpaper")
            for sntxKey in simpleFlawSntx.keys():
                simpleFlawSntx[sntxKey].append("\\ifnotpaper")

        if filename in SIMPLE_TEX_FILES:
            for flaw in flaws:
                smntcFlaw, sntxFlaw = getFlawGroups(flaw)
                simpleFlawSmntc[smntcFlaw].append(flaw)
                simpleFlawSntx[sntxFlaw].append(flaw)

                try:
                    labelGroup, label = re.search(
                        r"% Label ([A-Z]+) ([a-z\-]+)", flaw).groups()
                    for flawGroup, dict in [(smntcFlaw, simpleFlawSmntc),
                                            (sntxFlaw,  simpleFlawSntx)]:
                        dict[flawGroup] = [re.sub(
                            r"\s+% Label [A-Z]+ [a-z\-]+\s+",
                            "\n          ".join(
                                ["", "\\\\phantomsection{}", f"\\\\label{{{label}}}", ""]
                                if labelGroup == flawGroup.name else ["", ""]),
                            line) for line in dict[flawGroup]]
                except AttributeError:
                    continue
            
        if "extra" in filename:
            for smntcKey in simpleFlawSmntc.keys():
                simpleFlawSmntc[smntcKey].append("\\fi")
            for sntxKey in simpleFlawSntx.keys():
                simpleFlawSntx[sntxKey].append("\\fi")

        for flaw in flawCounts:
            sources = flaw.split("|")
            smntcFlaw, sntxFlaw = getFlawGroups(flaw)
            DEBUG = False

            sourceDicts = [categorizeSources(s) for s in sources]
            if DEBUG:
                print(sourceDicts, smntcFlaw.name, sntxFlaw.name)

            def inPairs(s, *, sFunc = None):
                if sFunc:
                    s = [{sFunc(x) for x in si} for si in s]
                return set.union(*(a & b for a, b in itertools.combinations(s, 2)))

            # These ensure that sources aren't double counted
            # Note that pieAdded is used based on the previous presentation of flaws by source tier
            # As of #138, this is now done as a table, but this naming convention is still used
            pieAdded, tableAdded = set(), set()
            def updateCounters(source, pieSec: str, r):
                nonlocal smntcFlaw, sntxFlaw

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
                    print(source, sourceCat, pieSec, r)

                if srcTuple not in tableAdded:
                    if type(flawDict[sourceCat].smntcFlaws[smntcFlaw]) is int:
                        flawDict[sourceCat].smntcFlaws[smntcFlaw] += 1
                        flawDict[sourceCat].sntxFlaws[sntxFlaw] += 1
                    else:
                        flawDict[sourceCat].smntcFlaws[smntcFlaw].addFlaw(r)
                        flawDict[sourceCat].sntxFlaws[sntxFlaw].addFlaw(r)
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
                for r, sources in sourceDicts[0].items():
                    if sources and isinstance(r, Rigidity):
                        updateCounters(str(list(map("".join, sources))), "groundTruth", r)
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
                            # Don't double count flaws within a single document
                            if (reduce(operator.mul, map(len, yearSets)) >
                                    len(inPairs(yearSets))):
                                updateCounters(author, "withinAuth", r)

                        for tup in {tuple(sorted([ai[0], bi[0]], key=getSrcCat))
                                for a, b in itertools.combinations(sets, 2)
                                for ai in a for bi in b if ai[0] != bi[0]}:
                            updateCounters(tup, "betweenCats", r)
            if DEBUG:
                printFlaws()

    for shortname, flawGroup in [("Smntc", simpleFlawSmntc),
                                    ("Sntx",  simpleFlawSntx)]:
        for k in flawGroup.keys():
            flawGroup[k] += ["\\ifnotpaper", "\\end{enumerate}", "\\else",
                                "\\end{itemize}", "\\fi"]
            writeFile(flawGroup[k], f"{shortname}Flaw{k.name.title()}", True)

    flawPies, flawTable = [], []
    smntcTotal, sntxTotal = [], []
    def totalHelper(total, new):
        return [a + b for a, b in itertools.zip_longest(
            total, [int(d.strip()) for d in new.split("%")], fillvalue=0)]

    for k, v in flawDict.items():
        smntcFlaws, sntxFlaws = v.getCatCounts(), v.getClsCounts()
        assert smntcFlaws.split("%")[-1] == sntxFlaws.split("%")[-1]

        smntcTotal = totalHelper(smntcTotal, smntcFlaws)
        sntxTotal  = totalHelper(sntxTotal, sntxFlaws)

        writeFile([smntcFlaws], f"{k.name.lower()}SmntcFlawBrkdwn", True)
        writeFile([sntxFlaws],  f"{k.name.lower()}SntxFlawBrkdwn", True)

        totalFlaws = sum({v.groundTruth, v.withinDoc, v.withinAuth,
                             sum(v.betweenCats.values())})

        slices = ([(v.groundTruth, "With a source of ground truth"),
                   (v.withinDoc, "Within a single document"),
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
        flawTable.append([f"\\{k.name.lower()}s{{}}"] + [val for val, _ in slices])
    
    writeFile([formatOutput(smntcTotal)], f"totalSmntcFlawBrkdwn", True)
    writeFile([formatOutput(sntxTotal)],  f"totalSntxFlawBrkdwn", True)

    flawPies.append(["\\begin{center}", "\\begin{subfigure}[t]{\\linewidth}",
                        "\\begin{tikzpicture}", "\\matrix [thick, draw=black] {",
                        "\\node[label=center:Legend] {{}}; \\\\"] +
                        [f"\\node[thick, shape=rectangle, draw=black, fill={DEFAULT_COLORS[i]}, label=right:{{{slice[1]}}}]({i}) {{}}; \\\\"
                        for i, slice in enumerate(slices)] +
                        ["};", "\\end{tikzpicture}", "\\end{subfigure}", "\\end{center}"])

    # From ChatGPT
    sepPieCharts: list[str] = []
    for i, item in enumerate(flawPies):
        sepPieCharts += item
        if i % 2:
            sepPieCharts.append("\\vskip\\baselineskip")
        else:
            sepPieCharts.append("\\hfill")

    flawCaption = "Sources of flaws based on \\hyperref[sources]{source tier}."
    writeFile(["\\begin{figure*}", "\\centering"] + sepPieCharts +
                [f"\\caption{{{flawCaption}}}",
                "\\label{fig:flawSources}", "\\end{figure*}"], "flawPies")

    writeLongtblr("flawTable", flawCaption,
                  ["Flaw between a document \\\\ from a \\hyperref[sources]{source tier} \\\\ below and a \\dots{}"] + [
                      f"\\rotatebox[origin=c]{{90}}{{{x}}}" for x in
                        [f"\\parbox{{3.5cm}}{{\\centering {x}}}" for x in 
                            ["source of \\\\ ground truth", "part of the same document",
                             "document with the same author"]] +
                        [cat.shortname.lower()[:-1] for cat in SrcCat  # Strip plural "s"
                            if cat.color.value >= 0]  # Exclude inferences and proposals
                  ], 
                  [" & ".join(map(str, x)) + " \\\\" for x in
                   # From https://stackoverflow.com/a/63080837/10002168
                   zip(*itertools.zip_longest(*flawTable, fillvalue="---"))],
                   toSort=False, rowHeadSpec="r", rowDataSpec="c")
