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
    META   = "``Meta-level'' Collections", "``Meta-level Sources''", Color.BLUE
    TEXT   = "Trusted Textbooks", "Textbooks", Color.MAROON
    OTHER  = "Other Sources", "Other Sources", Color.BLACK

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

        self.func, self.oat, self.rec, self.scal = 0, 0, 0, 0

        # self.other = {s : 0 for s in ["High", "Med", "Low"]}

    def __str__(self):
        return "\n".join(filter(None, [
            ", ".join(map(str, [self.withinSrc, self.withinAuth])),
            "Diffs: " + ", ".join([f"{k.name} {v}" for k, v in self.betweenCats.items()]),
            " | ".join(map(str, [self.syns, self.pars, self.cats])),
            " | ".join(map(str, [self.func, self.oat, self.rec, self.scal])),
            # "Other: " + ", ".join([f"{k} {v}" for k, v in self.other.items()])
            ])) + "\n"

class DiscrepCat(Enum):
    SYNS = "Synonyms"
    PARS = "Parents"
    CATS = "Categories"
    MISC = "Standalone"

otherDiscFiles = {"chapters/05a_std_discreps.tex"}

texFileDiscreps = {
    "chapters/05e_cat_discreps.tex": DiscrepCat.CATS,
    "build/multiSyns.tex": DiscrepCat.SYNS,
    "chapters/05_discrepancies.tex": DiscrepCat.MISC,
    "chapters/05a_std_discreps.tex": DiscrepCat.MISC
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
                self.countDiscreps(
                    map(lambda x: categorizeSources(x), discrep.split("|")),
                    re.search(r"% Discrep count \(([A-Z]+)\):", discrep)[1]
                    if origType == DiscrepCat.MISC else origType,
                    other=filename in otherDiscFiles)

    def output(self):
        self.texDiscreps()
        for k, v in self.dict.items():
            writeFile([formatOutput(
                [k.longname] + [getattr(v, dc.name.lower()).output()
                                for dc in DiscrepCat if dc != DiscrepCat.MISC]+
                                [formatOutput([v.func, v.oat, v.rec, v.scal]), ""]
                )], f"{k.name.lower()}DiscBrkdwn", True)

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
        # catsAdded is for building pie charts
        # parsAdded is for building table
        catsAdded, parsAdded = set(), set()
        def updateCounters(source, pieSec: str, inc: int, r) -> bool:
            if type(source) is tuple:
                srcTuple = tuple(map(getSrcCat, source))
                source = " ".join(map(lambda x: x.name.capitalize(), srcTuple))
            else:
                srcTuple = tuple(map(getSrcCat, [source] * 2))
            sourceCat = srcTuple[0]

            if debug:
                print(source, sourceCat, pieSec, inc, r)

            if srcTuple not in parsAdded:
                discCatName = (discCat.name if type(discCat) is DiscrepCat
                               else discCat).lower()
                discCatAttr = getattr(self.dict[sourceCat], discCatName)
                if type(discCatAttr) is int:
                    setattr(self.dict[sourceCat], discCat.lower(),
                            discCatAttr + 1)
                else:
                    discCatAttr.addDiscrep(r)
                parsAdded.add(srcTuple)
            if source not in catsAdded and inc:
                try:
                    getattr(self.dict[sourceCat], pieSec)[srcTuple[1]] += inc
                except TypeError:
                    setattr(self.dict[sourceCat], pieSec,
                            getattr(self.dict[sourceCat], pieSec) + inc)
                catsAdded.add(source)
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
