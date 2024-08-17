from enum import Enum, auto
from aenum import AutoNumberEnum, OrderedEnum
import itertools

class Color(OrderedEnum):
    GREEN  = 3
    BLUE   = 2
    MAROON = 1
    BLACK  = 0

    def __str__(self):
        return self.name.lower()

class SrcCat(AutoNumberEnum):
    STD    = "Established Standards", "Standards", Color.GREEN
    META   = '"Meta-level" Collections', '"Meta-level Sources"', Color.BLUE
    TEXT   = "Trusted Textbooks", "Textbooks", Color.MAROON
    OTHER  = "Other Sources", "Other Sources", Color.BLACK

    def __init__(self, longname, shortname, color):
        self.longname  = longname
        self.shortname = shortname
        self.color     = color

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

class Rigidity(Enum):
    EXP = auto()
    IMP = auto()

def getRigidity(rigidity: Rigidity | list[Rigidity]):
    if isinstance(rigidity, list):
        if any(r not in Rigidity for r in rigidity):
            raise ValueError(f"Invalid rigidity value in {rigidity}.")
        return Rigidity.IMP if Rigidity.IMP in rigidity else Rigidity.EXP
    return rigidity

class ExpImpCounter:
    def __init__(self):
        self.dict = {k: 0 for k in list(Rigidity)}
    
    def __str__(self):
        return str(tuple(self.dict.values()))

    def addDiscrep(self, rigidity: Rigidity | list[Rigidity]):
        self.dict[getRigidity(rigidity)] += 1

class DiscrepCounter:
    def __init__(self, value):
        self.withinSrc  = 0
        self.withinAuth = 0
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

class DiscrepSourceCounter:
    def __init__(self):
        self.dict = {k : DiscrepCounter(k.value) for k in SrcCat}

    def __str__(self):
        return "\n".join(f"{k.name}: {v}" for k, v in self.dict.items())

    def countDiscreps(self, sourceDict):
        added = set()
        for i, j in itertools.product(list(Rigidity), repeat=2):
            try:
                parSet = set(sourceDict["par"][i])
                synSet = set(sourceDict["syn"][j])

                for tup in parSet & synSet:
                    if tup[0] not in added and "".join(tup) not in added:
                        tupSrc = getSrcCat(tup[0])
                        self.dict[tupSrc].withinSrc += 1
                        self.dict[tupSrc].pars.addDiscrep([i, j])
                        added.add("".join(tup))
                        print("".join(tup))

                for author in {auth for auth in
                                    {s[0] for s in parSet - synSet} &
                                    {s[0] for s in synSet - parSet}
                                if auth not in added or
                                getRigidity([i,j]) == Rigidity.EXP}:
                    authSrc = getSrcCat(author)
                    self.dict[authSrc].withinAuth += 1
                    self.dict[authSrc].pars.addDiscrep([i, j])
                    added.add(author)
                    print(author)

                for a, b in {tuple(sorted(
                        [parTup[0], synTup[0]], key=lambda x: getSrcCat(x).color))
                        for parTup in parSet for synTup in synSet
                        if parTup[0] != synTup[0]}:
                    discID = "".join(a) + " " + "".join(b)
                    if discID not in added:
                        aSrc = getSrcCat(a)
                        self.dict[aSrc].betweenCats[getSrcCat(b)] += 1
                        self.dict[aSrc].pars.addDiscrep([i, j])
                        added.add(discID)
                        print(discID)

            except KeyError:
                continue