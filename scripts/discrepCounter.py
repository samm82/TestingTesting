import re
from aenum import AutoNumberEnum, Enum, OrderedEnum
from functools import reduce, total_ordering
import itertools
import operator

from helpers import Rigidity, categorizeSources, writeFile

class Color(OrderedEnum):
    GREEN  = 3
    BLUE   = 2
    MAROON = 1
    BLACK  = 0

    def __str__(self):
        return self.name.lower()

@total_ordering
class SrcCat(AutoNumberEnum):
    STD    = "Established Standards", "Standards", Color.GREEN
    META   = "``Meta-level'' Collections", "``Meta-level'' Documents", Color.BLUE
    TEXT   = "Trusted Textbooks", "Textbooks", Color.MAROON
    OTHER  = "Other Sources", "Other Documents", Color.BLACK

    def __init__(self, longname, shortname, color):
        self.longname  = longname
        self.shortname = shortname
        self.color     = color

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.color < other.color
        return NotImplemented

def getSrcCat(s) -> SrcCat:
    if any(std in s for std in {"IEEE", "ISO", "IEC"}):
        return SrcCat.STD
    if any(metastd in s for metastd in
        {"Washizaki", "Bourque and Fairley", "SWEBOK",
            "Hamburg and Mogyorodi", "ISTQB", "Firesmith"}):
        return SrcCat.META
    if any(textbook in s for textbook in
        {"van Vliet", "vanVliet", "Patton", "Peters and Pedrycz",
            "PetersAndPedrycz"}):
        return SrcCat.TEXT
    return SrcCat.OTHER

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

    def output(self):
        return formatOutput(self.dict.values())

    def addDiscrep(self, rigidity: Rigidity | list[Rigidity]):
        self.dict[getRigidity(rigidity)] += 1

class DiscrepCounter:
    def __init__(self, value):
        self.withinSrc, self.withinAuth = 0, 0
        # Differences between two categories; may be within the same category
        self.betweenCats = {k : 0 for k in SrcCat if k.value <= value}

        self.syns = ExpImpCounter()
        self.pars = ExpImpCounter()
        self.cats = ExpImpCounter()

        # self.other = {s : 0 for s in ["High", "Med", "Low"]}

    def __str__(self):
        return "\n".join(filter(None, [
            ", ".join(map(str, [self.withinSrc, self.withinAuth])),
            "Diffs: " + ", ".join([f"{k.name} {v}" for k, v in self.betweenCats.items()]),
            " | ".join(map(str, [self.syns, self.pars, self.cats])),
            # "Other: " + ", ".join([f"{k} {v}" for k, v in self.other.items()])
            ])) + "\n"

class DiscrepCat(Enum):
    SYNS = "Synonyms"
    PARS = "Parents"
    CATS = "Categories"
    MISC = "Standalone"
    OTHER = "Other"

otherDiscFiles = {"chapters/05a_std_discreps.tex"}

texFileDiscreps = {
    "build/multiSyns.tex": DiscrepCat.SYNS,
    "chapters/05_discrepancies.tex": DiscrepCat.MISC,
    "chapters/05a_std_discreps.tex": DiscrepCat.MISC,
    "chapters/05b_meta_discreps.tex": DiscrepCat.MISC,
    "chapters/05c_text_discreps.tex": DiscrepCat.MISC,
    "chapters/05d_other_discreps.tex": DiscrepCat.MISC,
    "chapters/05e_cat_discreps.tex": DiscrepCat.CATS,
}

class DiscrepSourceCounter:
    def __init__(self):
        self.dict = {k : DiscrepCounter(k.value) for k in SrcCat}

    def __str__(self):
        return "\n".join(f"{k.name}: {v}" for k, v in self.dict.items())

    def texDiscreps(self):
        for filename, origType in texFileDiscreps.items():
            with open(filename, "r") as file:
                content = [line for line in file.readlines()
                        if "% Discrep count" in line]
                
            for discrep in content:
                discType = (re.search(r"% Discrep count \(([A-Z]+)\):", discrep)[1]
                            if origType == DiscrepCat.MISC else origType)
                self.countDiscreps(
                    map(lambda x: categorizeSources(x), discrep.split("|")),
                    discType, discType == "OTHER")

    def output(self):
        self.texDiscreps()
        pieCharts = []
        for k, v in self.dict.items():
            writeFile([formatOutput(
                [k.longname] + [getattr(v, dc.name.lower()).output()
                                for dc in [DiscrepCat.SYNS, DiscrepCat.PARS,
                                           DiscrepCat.CATS]]
                )], f"{k.name.lower()}DiscBrkdwn", True)

            totalDiscreps = sum({v.withinSrc, v.withinAuth,
                                 sum(v.betweenCats.values())})

            slices = ([(v.withinSrc, "Within a single document"),
                       (v.withinAuth, "Between documents by the same author(s) or standards organization(s)")] +
                      [(catCount, "Between a document from this category and " +
                                  ("an" if cat.shortname.startswith("Other") else "a ") +
                                  cat.shortname.lower()[:-1])
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
                             f"\\caption{{Discrepancies found in {k.shortname.lower().replace(" ", "\\\\")}.}}",
                             f"\\label{{fig:{k.name.lower()}DiscrepSources}}",
                              "\\end{subfigure}"
                              ])
        
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

    def countDiscreps(self, sourceDicts, discCat: str | DiscrepCat,
                      other: bool = False, debug: bool = False):
        sourceDicts = list(sourceDicts)
        if debug:
            print(sourceDicts, discCat)

        def inPairs(s, *, sFunc = None):
            if sFunc:
                s = [{sFunc(x) for x in si} for si in s]
            return set.union(*(a & b for a, b in itertools.combinations(s, 2)))

        # These ensure that sources aren't double counted
        pieAdded, tableAdded = set(), set()
        def updateCounters(source, pieSec: str, inc: int, r) -> bool:
            if type(source) is tuple:
                srcTuple = tuple(map(getSrcCat, source))
                source = " ".join(map(lambda x: x.name.capitalize(), srcTuple))
            else:
                srcTuple = tuple(map(getSrcCat, [source] * 2))
            sourceCat = srcTuple[0]

            if debug:
                print(source, sourceCat, pieSec, inc, r)

            if srcTuple not in tableAdded and not other:
                discCatName = (discCat.name if type(discCat) is DiscrepCat
                               else discCat).lower()
                discCatAttr = getattr(self.dict[sourceCat], discCatName)
                if type(discCatAttr) is int:
                    setattr(self.dict[sourceCat], discCat.lower(),
                            discCatAttr + 1)
                else:
                    discCatAttr.addDiscrep(r)
                tableAdded.add(srcTuple)
            if source not in pieAdded and inc:
                try:
                    getattr(self.dict[sourceCat], pieSec)[srcTuple[1]] += inc
                except TypeError:
                    setattr(self.dict[sourceCat], pieSec,
                            getattr(self.dict[sourceCat], pieSec) + inc)
                pieAdded.add(source)
                if debug:
                    print(f"{pieSec}:", source)
                return True
            return False

        GROUP_SIZE = 2
        if len(sourceDicts) == 1:
            for r in list(Rigidity):
                try:
                    sources = sourceDicts[0][r]
                except KeyError:
                    continue

                if sources:
                    updateCounters(str(list(map("".join, sources))),
                                   "withinSrc", 1, r)

        else:
            for dicts in itertools.combinations(sourceDicts, r=GROUP_SIZE):
                for r in itertools.product(list(Rigidity), repeat=GROUP_SIZE):
                    try:
                        sets = [set(s[xi]) for s, xi in zip(dicts, r)]
                    except KeyError:
                        continue

                    for source in inPairs(sets, sFunc="".join):
                        updateCounters(source, "withinSrc", 1, r)

                    for author in inPairs(sets, sFunc=lambda x: x[0]):
                        yearSets = [{y for a, y in s if a == author} for s in sets]
                        # Finds number of discrepancies between author's documents
                        # unless within a single document; those have been counted
                        inc = (reduce(operator.mul, map(len, yearSets)) -
                                len(inPairs(yearSets)))

                        if (updateCounters(author, "withinAuth", inc, r) and debug):
                            print("years: ", yearSets)
                            print("   increase:", inc)

                    for tup in {tuple(sorted([ai[0], bi[0]], key=getSrcCat))
                            for a, b in itertools.combinations(sets, 2)
                            for ai in a for bi in b if ai[0] != bi[0]}:
                        updateCounters(tup, "betweenCats", 1, r)
        if debug:
            print(self)
            print()
