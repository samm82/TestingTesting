from copy import deepcopy
from math import ceil
import numpy as np
import itertools
from pandas import read_csv
import re
from string import ascii_lowercase
import sys
from typing import Optional

from flawCounter import *
from helpers import *

# Whether or not to display information for pulling source information
# Will only display information for approaches containing the provided string
DEBUG_SOURCE: str = ""

def debugSource(x, toPrint = ""):
    if isinstance(x, bool):
        if x:
            print(toPrint if toPrint else x)
    elif DEBUG_SOURCE and any(DEBUG_SOURCE in y for y in x):
        print(toPrint if toPrint else x)
        return True
    else:
        return False    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ApproachGlossary.py <filename>")
        sys.exit(1)
    
    csvFilename = sys.argv[1]

approaches = read_csv(csvFilename)
names = approaches["Name"].to_list()
categories = approaches["Approach Category"].to_list()
parents = approaches["Parent(s)"].to_list()
synonyms = approaches["Synonym(s)"].to_list()

# Write number of qualities to a file
writeFile([len(read_csv("QualityGlossary.csv")["Name"].to_list())],
          "qualityCount", True)

# Terms in parentheses we want to keep
PAREN_EXC = {"Acceptance"}

def processCol(col, sortByLen: bool=False):
    SOURCE_CHUNKS = [AUTHOR_REGEX, YEAR_REGEX, BEGIN_INFO_REGEX]

    # Adds a comma and a space to a RegEx within a non-capturing group
    def cs(regex):
        return fr"(?:{regex}, )"

    def copySources(x):
        out = debugSource(x)

        # "Pull" sources back (i.e., when a source applies to multiple items)
        for i in range(len(x)-1, 0, -1):
            debugSource(out, x[i])
            if x[i].find("(", 1) > 0:
                debugSource(out, x[i].split(" (")[-1])
            if (x[i].find("(", 1) > 0 and
                    not re.search(fr"{cs(AUTHOR_REGEX)}|({BEGIN_INFO_REGEX} )", x[i-1])):
                x[i-1] += f" ({x[i].split(" (")[-1]}"
            x[i] = x[i].replace("if they exist", "if it exists")

        # Pre-compile RegEx patterns
        IMPLIED_PATTERNS = [re.compile(fr"({PREFIX_REGEX})({r})")
                            for r in [BEGIN_INFO_REGEX, YEAR_REGEX]]
        HAS_AUTHOR_REGEX = re.compile(cs(AUTHOR_REGEX))

        # "Push" sources forward (i.e., when parts of a source are implied)
        while True:
            origX = x.copy()
            for i in range(1, len(x)):
                for j, pattern in enumerate(IMPLIED_PATTERNS):
                    search = pattern.search(x[i])
                    if search:
                        debugSource(out, ["BEGIN", "YEAR"][j])
                        debugSource(out, f"Search: {search.group()} -> {search.groups()}")
                        if (len(search.groups()) == 2 and
                                not HAS_AUTHOR_REGEX.search(x[i].split(search.group())[0])):
                            toPush = re.findall(f"({"?".join(
                                cs(c) for c in SOURCE_CHUNKS[:2-j]
                            )})", x[i-1])
                            debugSource(out, f"regex {f"({"?".join(
                                cs(c) for c in SOURCE_CHUNKS[:2-j]
                            )})"} applied to {x[i-1]}")
                            if toPush:
                                debugSource(out, f"new: {toPush[-1].join(search.groups())}")
                                x[i] = x[i].replace(search.group(),
                                                    toPush[-1].join(search.groups()))
            debugSource(out, x)
            if origX == x:
                return x

    for i, row in enumerate(col):
        if isinstance(row, str):
            # Remove exceptions from column as to not affect processing
            for exc in PAREN_EXC:
                row = row.replace(f"({exc}) ", "")
            col[i] = re.split(SPLIT_REGEX, row)
        else:
            col[i] = []

    if sortByLen:
        return [sorted(copySources(x), key=len) for x in col]
    return [copySources(x) for x in col]

names = [n.strip() for n in names if isinstance(n, str)]
# Sort entries for alphabetical order in multiCats rable
categories = processCol(categories, True)
parents = processCol(parents)
synonyms = processCol(synonyms)

staticApproaches = {
    'ConcreteExecution', 'SymbolicExecution', 'InductiveAssertionMethods',
    'ContentChecking', 'ModelVerification'}
staticKeywords = {'Audit', 'Inspection' 'Proof', 'Review', 'Static', 'Walkthrough'}
dynamicExceptions = {}

categoryDict = {
    "Approach": ([], []),
    "Level": ([], []),
    "Practice": ([], []),
    "Static": ([], []), # Not a category in the same way, but makes for easier code
    "Technique": ([], []),
    "Type": ([], []),
}

warned_multi_unsure = set()
# only == True returns a string iff the passed `name` is not explicit
def isUnsure(name: str, only: bool = False) -> Optional[str]:
    unsureTerms = {"?", " (Testing)"}.union(f"({term}" for term in IMPLICIT_KEYWORDS)
    if not only:
        unsureTerms.update(f" {term}" for term in IMPLICIT_KEYWORDS)

    outTerms = {unsure for unsure in unsureTerms if unsure in name}
    # Ignore the terms with distinct meanings when checking for multiple implicit keywords
    if (len(outTerms.difference({"?", " inferred"})) > 1 and
            name not in warned_multi_unsure):
        print(f"Multiple implicit keywords in {name}.")
        warned_multi_unsure.add(name)

    return (sorted(outTerms, key=name.index, reverse=True)[0]
            if outTerms else None)

def addLineToCategory(key, line):
    if line not in categoryDict[key][1] and "-> ;" not in line:
        categoryDict[key][1].append(line)

def removeInParens(s: str, stripInit: bool=False):
    s = s.replace(" (Testing)", " Testing")
    # s = re.sub(r" \(.*?\) \(.*?\)", "", s)
    # Remove nested parentheses first, if they exist
    s = re.sub(r" \([^\)]*\([^\)]*\)[^\)]*\)", "", s)
    s = re.sub(r"\([^\)]*\([^\)]*\)[^\)]*\)", "", s)
    s = re.sub(r" \(.*?\)", "", s)

    if stripInit:
        s = re.sub(r"\(.*?\)", "", s)

    if "(" not in s:
        s = s.strip(")")
    return s.replace("?", "")

def lineBreak(s: str) -> str:
    s = s.replace("/Some", "/<br/>Some")
    return f"<{s.replace(" ", "<br/>")}>"

def formatApproach(s: str, stripInit=False):
    s = removeInParens(s, stripInit)
    for c in "?-/() ":
        s = s.replace(c, "")
    s = s.replace("0", "Zero")
    s = s.replace("1", "One")
    return s.strip(",")

def addNode(name, style = "", key = "Approach", cat = ""):
    dashed = isUnsure(name, only=True)
    infer = False
    if key in cat:
        infer = ("Example" not in csvFilename and
                 ("(inferred" in cat or "(" not in cat))
        if not infer:
            dashed = dashed or isUnsure(cat, only=True)
    if dashed:
        name = name.replace("?", "")

    for exc in PAREN_EXC:
        if exc in name:
            splitName = name.split(f"({exc})")
            name = f"({exc})".join(map(removeInParens, splitName))
        else:
            name = removeInParens(name)

    extras = [f"label={lineBreak(name)}"]
    styles = [s for s in ["dashed" if dashed else "", style] if s]
    if styles:
        extras.append(f'style="{",".join(styles)}"')
    if infer:
        extras.append("color=grey")
    nameLine = f"{formatApproach(name)} [{",".join(extras)}];"

    for k in staticKeywords:
        if k in name and name not in dynamicExceptions:
            categoryDict["Static"][0].append(name)
            staticApproaches.add(formatApproach(name))
            break
    
    if style == "filled" and key == "Static":
        addLineToCategory("Static", nameLine)
        return

    if formatApproach(name) in staticApproaches:
        addLineToCategory("Static", nameLine)
    addLineToCategory(key, nameLine)

# Old criteria
# criteria = (name in {
#     "Capacity Testing", "Data-driven Testing", "Error Guessing",
#     "Endurance Testing", "Experience-based Testing", "Attacks",
#     "Exploratory Testing", "Fuzz Testing", "Load Testing",
#     "Model-based Testing", "Mutation Testing",
#     "Performance Testing", "Stress Testing"} or any(
#         re.match(r"Type \(implied by Firesmith, 2015, p\. 5[3-8].*\)", c)
#         for c in category))

# criteria = not any(t in "".join(category) for t in {"?", "Artifact"})

# criteria = not "Artifact" in "".join(category)

# Placeholder criteria for automatically tracking category flaws
criteria = True

class MultiCatInfo():
    def __init__(self, name, capHelper) -> None:
        self.name = name
        self.caption = (f"Test approaches {capHelper} more than one " +
                         "\\hyperref[cats-def]{category}.")
        self.lines: list[str] = []
        self.lenTotals: list[tuple[int, int]] = []

    def addMultiCatLine(self, flaw: str, name: str, catCells: list[str]):
        self.lenTotals.append(tuple(map(len, catCells)))
        self.lines.append(flaw + (" & ".join([removeInParens(name)] +
                                                catCells)) + "\\\\")

    def getColWidths(self) -> list[int]:
        avgLens = [ceil(n / len(self.lines))
                   for n in map(sum, zip(*self.lenTotals))]
        return [round(n * len(avgLens) / sum(avgLens), 2) for n in avgLens]

    def output(self):
        writeTblr(multiCat.name, multiCat.caption,
                      ["Approach", "Category 1", "Category 2"],
                      multiCat.lines, widths=multiCat.getColWidths()
        )

multiCatDict = {0 : MultiCatInfo("infMultiCats", "inferred to have"),
                1 : MultiCatInfo("multiCats",    "with")}

LONG_ENDINGS = {"Testing", "Management", "Scanning", "Audits",
               "Guessing", "Correctness"}
LONG_ENDINGS_REGEX = re.compile(r' \b(' + '|'.join(LONG_ENDINGS) + r')\b')

for name, category in zip(names, categories):
    for cat in category:
        for key in categoryDict.keys():
            if key in cat or key == "Approach":
                categoryDict[key][0].append(removeInParens(name))
                addNode(name, key=key, cat=cat)

    category = [c for c in category
                if not any(t in c for t in {"Approach", "Artifact"})]
    if len(category) > 1:
        flawCount = (getFlawCount(category, "CONTRA", "CATS")
                        if not any("?" in c for c in category) else "")
        multiCatDict[bool(flawCount)].addMultiCatLine(
            flawCount, # if criteria else "",
            # Add line breaks to longer test approaches
            f"{{{LONG_ENDINGS_REGEX.sub(r'\\\\\1', name)}}}",
            [formatLineWithSources(c, False) for c in category]
        )

if "Example" not in csvFilename:
    for multiCat in multiCatDict.values():
        multiCat.output()

for key in categoryDict.keys():
    categoryDict[key][1].append("")

def addToIterable(s, iterable, key=key):
    if isinstance(iterable, list):
        if removeInParens(s) not in iterable:
            addNode(s, style="dotted", key=key)
            iterable.append(removeInParens(s))
    elif isinstance(iterable, set):
        if formatApproach(s) not in iterable:
            addNode(s, style="filled", key=key)
            iterable.add(formatApproach(s))
    else:
        raise ValueError(f"addToIterable unimplemented for {type(iterable)}")

# Returns a tuple with the color for the rigid relations (if any),
# then for the unsure ones (if any)
def getRelColor(name: str) -> tuple[str]:
    def getSourceColor(s):
        return getSrcCat(s, rel=True).color

    if isUnsure(name, only=True):
        return (None, getSourceColor(name))

    if not isUnsure(name):
        return (getSourceColor(name), None)

    colors = [getSourceColor(src) for src in name.split(isUnsure(name), 1)]
    return (colors[0], colors[1] if colors[1] > colors[0] else None)

def colorRelations(colors, edge, extra=""):
    out = []
    # Second iteration is for unsure relations
    for i, style in enumerate(['', 'style="dashed"']):
        if colors[i]:
            color = f'color="{colors[i]}"' if colors[i] != Color.BLACK else ""
            out.append(f"{edge}[{",".join(list(
                filter(None, [extra, style, color])))}];".replace("[]", ""))
    return out

# Add synonym relations
synDict, nameDict = {}, {}
synSets = {}
for name, synonym in zip(names, synonyms):
    rname, fname = removeInParens(name), formatApproach(name)
    for syn in synonym:
        rsyn, fsyn = removeInParens(syn), formatApproach(syn)
        if not (any(minor in syn.lower() for minor in {"spelled", "called"}) or
                (fsyn.isupper() and "Example" not in csvFilename)):
            nameWithSource = rname + ("?" if name.endswith("?") else "")
            if "(" in syn and syn.count(" (") != rsyn.count(" ("):
                source = syn.split(' (')
                for i in range(source[-1].count(")"), 0, -1):
                    nameWithSource += " (" + source[-i]
            try:
                synDict[rsyn].append(nameWithSource)
            except KeyError:
                synDict[rsyn] = [nameWithSource]
            try:
                nameDict[nameWithSource].append(rsyn)
            except KeyError:
                nameDict[nameWithSource] = [rsyn]
            # To only track relation one way and check inconsistencies
            try:
                if synSets[f"{fname} -> {fsyn}"] != getRelColor(syn):
                    raise ValueError(
                        f"Mismatch between rigidity of synonyms {fsyn} and {fname}")
            except KeyError:
                synSets[f"{fsyn} -> {fname}"] = getRelColor(syn)

nameDict.update(synDict)

paperExamples = {"Invalid Testing", "Soak Testing", "User Scenario Testing",
                 "Link Testing"}

multiSynNotes = {
    "Reliability Testing": (
        "Endurance testing is given as a child of reliability testing by "
        "\\citet[p.~55]{Firesmith2015}, although the terms are not synonyms."
    ),
    "Static Assertion Checking": (
        "% Flaw count (WRONG, SYNS): {ChalinEtAl2006} | {LahiriEtAl2013} \n\t\t"
        "\\citet[p.~343]{ChalinEtAl2006} \\multiAuthHelper{list} "
        "\\ifnotpaper \\acf{rac} and \\acf{sv} \\else Runtime Assertion Checking "
        "\\acf{rac} and Software Verification \\acf{sv} \\fi "
        "as ``two complementary forms of assertion checking''; "
        "based on how the term ``static assertion checking'' is used by "
        "\\citet[p.~345]{LahiriEtAl2013}, it seems like this should be the "
        "complement to \\acs{rac} instead."
    ),
    "Operational Testing": (
        "% Flaw count (CONTRA, SYNS): ISTQB | {Firesmith2015} \n\t\t"
        "``Operational'' and ``production acceptance testing'' are treated as "
        "synonyms by \\citetISTQB{} but listed separately by \\citet[p.~30]{Firesmith2015}."
    ),
    "Production Verification Testing": (
        "``Production acceptance testing'' \\citep[p.~30]{Firesmith2015} seems "
        "to be the same as ``production verification testing'' "
        "\\citep[p.~22]{IEEE2022} but neither is defined."
    )
}

noteOnSource = {"Operational Testing"}

expMultiSyns, impMultiSyns, infMultiSyns = [], [], []
def makeMultiSynLine(valid, syn, terms, alsoSyns):
    if any("(" not in term for term in terms):
        multiSynsList = infMultiSyns
    else:
        multiSynsList = (impMultiSyns if not all(
            synSets[f"{fsyn} -> {term}"][0] for term in valid)
            else expMultiSyns)

    def processTerm(term):
        emph = term in alsoSyns
        term = term.split(" (")
        if term[0] in multiSynNotes.keys():
            term[term[0] in noteOnSource] += f"\\footnote{{{multiSynNotes[term[0]]}}}"
        if emph:
            term[0] = f"\\emph{{{term[0]}}}"
        term = " (".join(term)
        return f"\t\t\\item {term}"

    line = "\n".join([f"\\item \\textbf{{{syn}:}}",
                      f"{getFlawCount(terms, "CONTRA", "SYNS")}\\begin{{itemize}}"] +
                      list(map(processTerm, terms)) + ["\t\\end{itemize}"])
    if syn not in paperExamples:
        line = "\n".join(["\\ifnotpaper", line, "\\fi"])

    multiSynsList.append(formatLineWithSources(line))

for key in categoryDict.keys():
    for syn, terms in synDict.items():
        fsyn = formatApproach(syn)
        knownTerm = lambda x: removeInParens(x) in categoryDict[key][0]
        if (knownTerm(syn) or (sum(1 for x in terms if knownTerm(x)) > 1)):
            validTerms = [term for term in terms
                          if (f"{fsyn} -> {formatApproach(term)}"
                              in synSets.keys())
                          and knownTerm(term)]
            if validTerms:
                if key == "Approach" and (len(validTerms) > 1):
                    alsoSyns = []
                    for x, y in itertools.combinations(validTerms, 2):
                        fx, fy = formatApproach(x), formatApproach(y)
                        if any(rel in synSets.keys() for rel in {
                                f"{fx} -> {fy}", f"{fy} -> {fx}"}):
                            alsoSyns.append((x, y))
                    if len(alsoSyns) < len(validTerms) - 1:
                        if len(alsoSyns) > 1:
                            raise NotImplementedError
                        makeMultiSynLine(map(formatApproach, validTerms),
                                         syn, list(filter(knownTerm, terms)),
                                         list(sum(alsoSyns, ())))
                addToIterable(syn, categoryDict[key][0], key)
                for term in validTerms:
                    addToIterable(term, categoryDict[key][0], key)

                    fterm = formatApproach(term)
                    for line in colorRelations(synSets[f"{fsyn} -> {fterm}"],
                                               f"{fterm} -> {fsyn}", "dir=none"):
                        addLineToCategory(key, line)

    if categoryDict[key][1][-1] != "":
        categoryDict[key][1].append("")

    # ONLY USE SAME RANK FOR THESE CATEGORIES
    if key in {}:
        blacklistSyns = set()
        for name, syns in nameDict.items():
            if (len(syns) == 1 and name in categoryDict[key][0] and
                    name not in blacklistSyns and syns[0] in categoryDict[key][0]):
                addLineToCategory(key, f'{{rank=same {formatApproach(
                    name)} {formatApproach(syns[0])}}}')
                print(key, name, syns[0])
                blacklistSyns.update({name, syns[0]})
        if blacklistSyns:
            categoryDict[key][1].append("")

for synList in [expMultiSyns, impMultiSyns, infMultiSyns]:
    synList.sort(key=lambda x: re.sub(r"\(.+\) ", "", x))
    synList.sort(key=lambda x: x.count("\\item"), reverse=True)

if "Example" not in csvFilename:
    writeFile(expMultiSyns + impMultiSyns, "multiSyns", True)
    writeFile(sorted(infMultiSyns, key=lambda x: x.count("\\cite"), reverse=True),
            "infMultiSyns", True)

workingStaticSet = staticApproaches.copy()

selfCycles = []
# Add parent relations
for name, parent in zip(names, parents):
    fname = formatApproach(name)
    for par in parent:
        fpar = formatApproach(par, stripInit=True)
        if not fpar.replace(" ", ""):
            continue
        if fname == fpar:
            selfCycles.append(par)

        for key in categoryDict.keys():
            for parentLine in colorRelations(
                    getRelColor(par), f"{fname} -> {fpar}"):
                if key == "Static" and (fname in staticApproaches or
                                        fpar in staticApproaches):
                    addToIterable(name, workingStaticSet, "Static")
                    addToIterable(par, workingStaticSet, "Static")
                    addLineToCategory("Static", parentLine)
                elif (removeInParens(name) in categoryDict[key][0] and
                    removeInParens(par) in categoryDict[key][0]):
                    addLineToCategory(key, parentLine)

print()

selfCycleCount = len(selfCycles)

if "Example" not in csvFilename:
    selfCycles = [f"\\item {getFlawCount([cycle], "WRONG", "PARS")}{formatLineWithSources(cycle)}"
                  for cycle in selfCycles]
    writeFile(["\\begin{enumerate}"] + selfCycles + ["\\end{enumerate}"],
              "selfCycles", True)

def splitListAtEmpty(listToSplit):
    recArr = np.array(listToSplit)
    return [subarray.tolist() for subarray in
            np.split(recArr, np.where(recArr == "")[0]+1)
            if len(subarray) > 0]

# Not stable; MUST be in correct order for table footnotes
parSynNotes = {
    ("Fault Tolerance Testing", "Robustness Testing") :
        {"footnote": "\\ftrnote{}"},
    ("Functional Testing", "Specification-based Testing") :
        {"footnote": "\\specfn{}"},
    # ("Performance Testing", "Performance-related Testing") :
    #     {"footnote": "See \\Cref{perf-test-ambiguity}."},
    ("Use Case Testing", "Scenario Testing") :
        {"footnote": "\\ucstn{}"},
    ("Organization-based Testing", "Role-based Testing") :
        {"footnote": "The distinction between organization- and role-based "
            "testing in \\citep[pp.~17, 37, 39]{Firesmith2015} seems "
            "arbitrary, but further investigation may prove it to be meaningful.",
        "todo": "\\thesisissueref{59}"},
    ("Structured Walkthroughs", "Walkthroughs") :
        {"footnote": "See \\flawref{walkthrough-syns}."},
    ("Exploratory Testing", "Unscripted Testing") :
        {"label": "exp-unscrip"}
}

parSyns, infParSynsParSrc, infParSynsSynSrc, infParSynsNoSrc = \
    set(), set(), set(), set()

# Iterator to get next letter for footnotes
letters = iter(ascii_lowercase)
tableFootnotes: list[str] = []

manualInfParSyns = {("Dynamic Analysis", "Dynamic Testing")}
# Since TblrNote uses unique footnotes, this is needed to avoid duplicates
addedParSyns: set[tuple[str, str]] = set()

def makeParSynLine(chd, par, parSource, synSource) -> None:
    # Don't add manually tracked or already-tracked parSyns to table
    if any((chd, par) in s for s in [manualInfParSyns, addedParSyns]):
        return
    addedParSyns.add((chd, par))

    parSource = formatLineWithSources(parSource, False)
    synSource = formatLineWithSources(synSource, False)

    def processChd(chd, note):
        # Refactored by GitHub Copilot
        label = note.get("label")
        if label:
            return f"\\phantomsection{{}}\\label{{{label}}}{chd}"
        return chd

    if not (parSource and synSource):
        if parSource:
            parSynSet = infParSynsParSrc
        elif synSource:
            parSynSet = infParSynsSynSrc
        else:
            parSynSet = infParSynsNoSrc
        for terms, note in parSynNotes.items():
            # Processing for list version
            if chd == terms[0] and par == terms[1]:
                try:
                    par += note["todo"]
                except KeyError:
                    pass
                try:
                    par += f"\\footnote{{{note["footnote"]}}}"
                except KeyError:
                    pass
                chd = processChd(chd, note)
                break
        parSynSet.add(f"\\item {chd} $\\to$ {par} {parSource or synSource or ""}")
        return

    for terms, note in parSynNotes.items():
        # Processing for table version
        if chd == terms[0] and par == terms[1]:
            try:
                tableFootnotes.append(note["footnote"])
                par += f"\\TblrNote{{{next(letters)}}}"
            except KeyError:
                pass
            chd = processChd(chd, note)
            break
    parSyns.add(getFlawCount([parSource, synSource], "CONTRA", "PARS") +
                f"{chd} $\\to$ {par} & {parSource} & {synSource} \\\\")

splitAtEmpty = splitListAtEmpty(categoryDict["Approach"][1])
# Don't look for parent/synonym flaws unless both are present
parentLines = splitAtEmpty[-1] if len(splitAtEmpty) > 2 else []
for chd, syns in nameDict.items():
    par: str
    for par in syns:
        synLines = [p for p in parentLines if p.startswith(
            f"{formatApproach(chd)} -> {formatApproach(par)}")]
        if synLines:
            if chd in synDict.keys():
                synSource = par.split("(", 1)
                par = removeInParens(par)
            else:
                synSource = chd.split("(", 1)
                chd = removeInParens(chd)

            nameLookup = [name for name in names if name.startswith(chd)]
            if len(set(nameLookup)) != 1:
                raise ValueError(
                    f"Problem with finding child term '{removeInParens(chd)}' in `names`")
            parSource = [parItem for parItem in parents[names.index(nameLookup[0])]
                         if parItem.startswith(par)]
            if len(parSource) != 1:
                raise ValueError(
                    "Problem with finding source for parent relation between "
                     f"'{removeInParens(chd)}' and '{removeInParens(par)}'")
            parSource = parSource[0].split("(", 1)

            parSource = "(" + parSource[-1] if len(parSource) > 1 else ""
            synSource = "(" + synSource[-1] if len(synSource) > 1 else ""
            makeParSynLine(chd, par, parSource, synSource)

# Pairs with sources for both
parSynCount = "".join(parSyns).count("\\to")

if "Example" not in csvFilename:
    writeTblr(
        "parSyns",
        "Pairs of test approaches with a \\hyperref[par-chd-rels]{parent-child} \\emph{and} \\hyperref[syn-rels]{synonym} relation.",
        ["``Child'' $\\to$ ``Parent''", "Parent-Child Source(s)", "Synonym Source(s)"],
        list(parSyns),
        footnotes=tableFootnotes
    )

    writeFile([x for x in itertools.chain.from_iterable(itertools.zip_longest(
        map(lambda x: f"\\paragraph{{{x}}}",
            ["Pairs given a parent-child relation",
            "Pairs given a synonym relation",
            "Pairs that could have a parent/child \\emph{or} synonym relation"]),
        map(lambda x: "\n".join(["\\begin{enumerate}"] + list(
            map(lambda x: f"\t{x}", sortByImplied(x))) +
            ["\\end{enumerate}"]), [infParSynsParSrc, infParSynsSynSrc, infParSynsNoSrc])))],
            "infParSyns", True)

    writeFile([f"{formatCount(parSynCount)}% Pairs of terms with parent/child AND synonym relations",
            f"{formatCount(selfCycleCount)}% Self-cycles"],
            "parSynCounts", True)

class Flag(Enum):
    COLOR = auto()
    STYLE = auto()

def inLine(flag, style, line):
    return re.search(fr"label=.+,{flag.name.lower()}=.*{style}", line)

if "Example" not in csvFilename:
    outputFlaws()
    genFlawMacros(FlawDmn)
    genFlawMacros(FlawMnfst)

INVIS_EDGE_LINE = 'edge [style="invis"]'

def sameRank(lines):
    return ['{', 'rank=same'] + lines + ['}']

# Returns modified lines and generated legend
def makeLegend(lines, separate: bool=False) -> tuple[list[str], list[str]]:
    LONG_EDGE_LABEL = 'label="                "'

    # Only include meaningful synonyms
    syns = [line.split(" ")[0] for line in lines if inLine(Flag.STYLE, "dotted", line)]
    synsToRemove = [syn for syn in syns if sum(1 for line in lines if syn in line) < 3]
    lines = [line for line in lines if not any(syn in line for syn in synsToRemove)]

    impTerm, dynTerm = '', ''
    if any(inLine(Flag.STYLE, "dashed", line) for line in lines):
        impTerm = 'imp5 [label=<Implied<br/>Term> style="dashed"]'

    if any(inLine(Flag.STYLE, "filled", line) for line in lines):
        dynTerm = 'dyn [label=<Dynamic<br/>Approach> style="filled"]'

    twoSyn = [
        'syn3 [label=<Term>]',
        'syn4 [label=<Synonym<br/>to Both> style="dotted"]',
        'syn5 [label=<Term>]',
        'syn3 -> syn4 -> syn5 [dir=none]',
    ] if len(syns) > len(synsToRemove) else []

    def impOrDynWithSyn(nodes, forceDyn=False):
        if len(nodes) == 1:
            nodes = nodes[0]
        else:
            nodes = f'{{ {" ".join(nodes)} }}'
        return f'{'imp5' if impTerm and not forceDyn else 'dyn'} -> {nodes}'

    def twoSynAlign(nodes):
        synNodes = [f'syn{i}' for i in range(3, 6, 2 if len(nodes) == 2 else 1)]
        return [f'{synNode} -> {nodes[i]}' for i, synNode in enumerate(synNodes)]

    extras, align = [], []
    if impTerm and dynTerm:
        extras = sameRank([impTerm, dynTerm])
        align = [impOrDynWithSyn(["imp1", "imp2"]),
                impOrDynWithSyn(["imp3", "imp4"], forceDyn=True)]
        if twoSyn:
            extras += sameRank(twoSyn)
            align = twoSynAlign(align)
    elif twoSyn:
        align = twoSynAlign([f'imp{i}' for i in range(2, 5)])
        if not (impTerm or dynTerm):
            extras = sameRank(twoSyn)
            align += twoSynAlign([f'imp{i}' for i in range(1, 4)])
        else:
            extras = sameRank([impTerm if impTerm else dynTerm] + twoSyn)
            align = [impOrDynWithSyn(["imp1"])] + align
    elif impTerm or dynTerm:
        extras = [impTerm if impTerm else dynTerm]
        align = [impOrDynWithSyn(["imp2", "imp3"])]

    INDENT = "    "
    extras = [f'{INDENT if line in "}{" else 2*INDENT}{line}' for line in extras]

    srcCats = [srcCat for srcCat in SrcCat
                if any(srcCat.color.name.lower() in line for line in lines)]
    srcCats.append(SrcCat.PAPER)
    srcCats.sort(reverse=True)  # Sort in decreasing "trustworthiness"

    colors, colorRow = [], []
    prevAlignNodes = (sorted(set(a.split(" -> ")[0] for a in align)) or
                        [f"imp{i}" for i in range(1, 5)])
    if len(srcCats) < 2:
        prevAlignNodes = prevAlignNodes[1:-1]

    for i in range(0, len(srcCats) * 2, 2):
        colorRow += [f"src{i+1} [style=invis];", f"src{i+2} [style=invis];",
                f"src{i+1} -> src{i+2} [color={srcCats[i//2].color.name.lower()}, "
                f"label=<{srcCats[i//2].label}>]"]
        if i % 4:
            colors += sameRank(colorRow)
            colorRow = []
            newAlignNodes = [f"src{j}" for j in range(i-1, i+3)]
            align += [f"{a} -> {b}" for a, b in zip(newAlignNodes, prevAlignNodes)]
            prevAlignNodes = newAlignNodes
    if colorRow:
        colors += sameRank(colorRow)
        align += [f"{a} -> {b}" for a, b in
                    zip([f"src{j}" for j in range(i+1, i+3)], prevAlignNodes[1:])]

    # From https://stackoverflow.com/a/65443720/10002168
    return lines, [
        'margin=0' if separate else '',
        'subgraph cluster_legend {',
        '    margin=8' if separate else '',
        '    label="Legend";',
        # This puts the label at the top, not the bottom, because of the rankdir
        # Behaviour depends on if the legend is separate from the graph or not
       f'    labelloc="{"t" if separate else "b"}";',
        '    fontsize="48pt"',
        '    rankdir=BT' if separate else '',
        '    {',
        '        rank=same',
        '        chd [label="Child"];',
        '        par [label="Parent"];',
       f'        chd -> par [{LONG_EDGE_LABEL}];',
        '        syn1 [label="Synonym"];',
        '        syn2 [label="Synonym"];',
       f'        syn1 -> syn2 [dir=none {LONG_EDGE_LABEL}];',
        '    }',
        '    {',
        '        rank=same',
        '        imp1 [label="Child"];',
        '        imp2 [label=<Implied<br/>Parent>];',
       f'        imp1 -> imp2 [style="dashed" {LONG_EDGE_LABEL}]',
        '        imp3 [label=<Implied<br/>Synonym>];',
        '        imp4 [label=<Implied<br/>Synonym>];',
       f'        imp3 -> imp4 [style="dashed" dir=none {LONG_EDGE_LABEL}]',
        '    }',
    ] + extras + colors + [
        # For alignment
        INVIS_EDGE_LINE,
        'imp1 -> chd',
        'imp2 -> par',
        'imp3 -> syn1',
        'imp4 -> syn2',
    ] + align + ['}', ''] + ([] if separate else [
        '// Connect the dummy node to the first node of the legend',
        'start -> chd [style="invis"];'])

CUSTOM_LEGEND = {"subsumes", "specBased", "parChd", "recovery", "scalability", "Example"}

def writeDotFile(lines, filename):
    legend = []
    if all(name not in filename for name in CUSTOM_LEGEND):
        lines, legend = makeLegend(lines)

    lines = [
        "\\documentclass{article}",
        "\\usepackage{graphicx}",
        "\\usepackage[pdf]{graphviz}",
        "\\usepackage{tikz}",
        "\\usetikzlibrary{arrows,shapes}",
        "",
        "\\begin{document}",
        f"\\digraph{{{filename}}}{{",
    ] + (["rankdir=BT;", ""] if "rankdir" not in "\n".join(lines) else []) + ([
        "// Dummy node to push the legend to the top left",
        'start [style="invis"];', ""] if legend else []
    ) + lines + legend + [
        "}",
        "\\end{document}",
    ]

    writeFile(lines, filename)

if "Example" in csvFilename:
    writeDotFile(categoryDict["Static" if "Static" in csvFilename else "Approach"][1],
                 f"{csvFilename.split("/")[-1][:-4]}Graph")
    
    rigidDict = ({"ExampleGlossary": categoryDict["Approach"]}
                  if csvFilename.split("/")[-1] == "ExampleGlossary.csv"
                  else dict())
else:
    rigidDict = categoryDict

for key, value in rigidDict.items():
    lines = value[1]
    if key != "ExampleGlossary":
        writeDotFile(lines, f"{key.lower()}Graph")

    unsure = reduce(operator.add,
                    [[val] + [c.split()[0] for c in lines if inLine(flag, val, c)]
                    for flag, val in {(Flag.STYLE, "dashed"), (Flag.COLOR, "grey")}])

    writeDotFile([c for c in lines if all(x not in c for x in unsure)],
                f"rigid{key}Graph")

SYN = "syn"
class CustomGraph:
    PROPOSED_COLOR_TAG = "color=orange"

    def __init__(self, name, terms:set, add:dict = dict(),
                 remove:dict = dict(), synConstraint:bool = True):
        self.name = name
        self.terms = terms
        self.add = add
        self.remove = remove
        self._addRevSynsToRemove(deepcopy(remove))
        self.synConstraint = synConstraint

        # Update set of terms in case any get added
        self.terms.update(child for child in self.add.keys())
        self.terms.update(parent for parents in self.add.values()
                          for parent in parents)

    # This *might* not be necessary, but I'm keeping it just in case
    def _addRevSynsToRemove(self, toRemove=dict()):
        for chd, pars in toRemove.items():
            if isinstance(pars, list):
                for par in pars:
                    if isinstance(par, tuple) and par[0] == SYN:
                        try:
                            self.remove[par[1]].append((SYN, chd))
                        except KeyError:
                            self.remove[par[1]] = [(SYN, chd)]

    def inherit(self, child: 'CustomGraph'):
        self.add.update({chd: [par for par in pars if par in self.terms]
                         for chd, pars in child.add.items()
                         if chd in self.terms})
        self.remove.update(child.remove)
        self._addRevSynsToRemove(child.remove)

    def buildGraph(self):
        formattedTerms = [formatApproach(term) for term in self.terms]

        # Currently unused; finds ALL edges that contain ANY specified terms
        # Led to a lot of clutter
        # # Optimized with ChatGPT to remove redundant checks and extra new lines
        # lines = [line for line in categoryDict["Approach"][1]
        #          if any(term in line for term in formattedTerms) or line == ""]

        chunks = splitListAtEmpty(categoryDict["Approach"][1])
        if len(chunks) == 2:
            nodes = chunks[0]
            rels = chunks[1]
        elif len(chunks) == 3:
            nodes = chunks[0] + chunks[1]
            rels = chunks[1] + chunks[2]
        elif len(chunks) == 4:
            nodes = chunks[0] + chunks[1]
            rels = chunks[1] + chunks[2] + chunks[3]
        else:
            raise ValueError("Unexpected grouping of lines for automatic "
                            f"{self.name} graph")

        rels = [line.replace("dir=none", "dir=none,constraint=false")
                if not self.synConstraint else line
                for line in rels if line == "" or
                (line.split(" -> ")[0] in formattedTerms and
                line.split(" -> ")[1].split("[")[0].strip(";") in formattedTerms) or
                (line.split(" ")[1] in formattedTerms and
                line.split(" ")[2].strip("}") in formattedTerms)]
        nodes = [node for node in nodes if "->" not in node and
                 # Only include nodes if they *actually* appear in a relation
                 any(re.search(fr"\b{node.split(" ")[0]}\b", line)
                     for line in rels)]

        # Will be used to build legend
        allLines = nodes + rels
        writeDotFile(allLines, f"{self.name}Graph")

        if self.add:
            rels.append("")
            alreadyAdded = dict()
            for child, parents in self.add.items():
                for parent in parents:
                    relLine = f"{formatApproach(child)} -> {formatApproach(parent)}"
                    linesAlready = [rel for rel in rels if rel.startswith(relLine)]
                    if linesAlready:
                        alreadyAdded[f"{child} -> {parent}"] = linesAlready
                        continue
                    if child in self.terms and parent in self.terms:
                        rels.append(f"{relLine}[{self.PROPOSED_COLOR_TAG}];")
            if alreadyAdded:
                print("WARNING: the following lines already exist in the custom "
                      f"{self.name} graph but were attempted to be added:")
                for rel, lines in alreadyAdded.items():
                    print("\t", rel)
                    for line in lines:
                        print("\t\t", line)
                    input()

        for child, parents in self.remove.items():
            if isinstance(parents, list):
                def getParentFromTuple(t):
                    return t[1] if isinstance(t, tuple) else t

                rels = [rel for rel in rels if not rel.startswith(tuple(
                    f"{formatApproach(child)} -> {formatApproach(
                        getParentFromTuple(parent))}{"[dir=none" if isinstance(
                            parent, tuple) and parent[0] == SYN else ""}"
                    for parent in parents if child in self.terms and
                        getParentFromTuple(parent) in self.terms
                ))]
            elif isinstance(parents, bool) and parents:
                nodes = [node for node in nodes if not formatApproach(child) in node]
                rels  = [rel  for rel  in rels  if not formatApproach(child) in rel ]
                self.terms.discard(child)
            else:
                raise ValueError("Unexpected set of items to remove from "
                                 f"{self.name} graph")

        if self.add or self.remove:
            nodes = set(nodes)
            for term in self.terms:
                termLine = f"{formatApproach(term)} [label={lineBreak(term)}"
                if not {node for node in nodes if node.startswith(termLine)}:
                    nodes.add(f"{termLine},{self.PROPOSED_COLOR_TAG}];")
            nodes.discard("")

            # Filter out nodes with no relations
            nodes = {node for node in nodes if sum(map(
                lambda rel: node.split(" ")[0] in rel, rels
            ))}

            # Group nodes as in original 
            nodesList = sortIgnoringParens(list(
                node for node in nodes if not "dotted" in node)) + [""]
            nodesList += sortIgnoringParens(list(
                node for node in nodes if node not in nodesList)) + [""]

            writeDotFile(nodesList+rels, f"{self.name}ProposedGraph")
            allLines += nodesList+rels
        
        # TODO: 'Vertical' custom legends are hardcoded to be these two
        if self.name == "specBased":
            return
        elif self.name == "subsumes":
            horizontal = False
            # Share legend between subsumes and specBased
            subsumesGraph.inherit(specBasedGraph)
            subsumesGraph.name = "parChd"
        else:
            horizontal = True

        if self.name in CUSTOM_LEGEND:
            _, legend = makeLegend(allLines, separate=True)
            # From https://www.geeksforgeeks.org/python-split-list-into-lists-by-particular-value/
            splitLegend = [list(v) for k, v in itertools.groupby(
                               legend, lambda x: x != INVIS_EDGE_LINE)
                               if k]

            splitLegend[-1] = [" -> ".join(reversed(line.split(" -> ")))
                               for line in splitLegend[-1]
                               if not all(node in line for node in {"imp", "src"})]

            writeDotFile(splitLegend[0] + [INVIS_EDGE_LINE] + (
                (sameRank(["chd", "src1"]) + sameRank(["imp1", "src5"]))
                if horizontal else ["imp1 -> src1 -> src5"]) + splitLegend[-1],
                f"{self.name}Legend")

subsumesGraph = CustomGraph(
    "subsumes",
    {"All-C-Uses/Some-P-Uses Testing", "All-DU-Paths Testing",
     "All-Definitions Testing", "All-P-Uses Testing",
     "All-P-Uses/Some-C-Uses Testing", "All-Uses Testing",
     "Branch Condition Combination Testing", "Branch Condition Testing",
     "Branch Testing", "MC/DC Testing", "Path Testing", "Statement Testing",
     "Strong Mutation Testing", "Weak Mutation Testing"}
)

specBasedGraph = CustomGraph(
    "specBased",
    {"All Combinations Testing", "Base Choice Testing", "Boundary Value Analysis",
     "Cause-Effect Graphing", "Classification Tree Method","Combinatorial Testing",
     "Decision Table Testing", "Each Choice Testing", "Equivalence Partitioning",
     "Metamorphic Testing", "Pairwise Testing", "Random Testing",
     "Requirements-based Testing", "Scenario Testing", "Specification-based Testing",
     "State Transition Testing", "Syntax Testing", "Use Case Testing"},
     synConstraint=False
)

recoveryGraph = CustomGraph(
    "recovery",
    {"Availability Testing", "Backup and Recovery Testing", "Backup/Recovery Testing",
     "Disaster/Recovery Testing", "Failover Testing", "Failover/Recovery Testing",
     "Failure Tolerance Testing", "Fault Tolerance Testing", "Performance Testing",
     "Performance-related Testing", "Recoverability Testing", "Recovery Testing",
     "Reliability Testing", "Survivability Testing", "Usability Testing"},
    add = {
        "Backup and Recovery Testing" : ["Recoverability Testing"],
        "Recoverability Testing" : ["Availability Testing",
                                    "Failure Tolerance Testing",
                                    "Fault Tolerance Testing"],
        "Recovery Performance Testing" : ["Performance-related Testing",
                                          "Recoverability Testing"],
        "Transfer Recovery Testing" : ["Recoverability Testing"],
    },
    remove = {
        "Backup and Recovery Testing" : ["Reliability Testing"],
        "Failover/Recovery Testing" : True,
        "Recovery Testing" : True,
    }
)

scalabilityGraph = CustomGraph(
    "scalability",
    {"Capacity Testing", "Efficiency Testing", "Elasticity Testing",
     "Load Testing", "Memory Management Testing",
     "Performance Efficiency Testing", "Performance Testing",
     "Resource Utilization Testing", "Scalability Testing",
     "Stress Testing", "Transaction Flow Testing", "Volume Testing"},
    # add = {
    #     "Backup and Recovery Testing" : ["Recoverability Testing"],
    #     "Recoverability Testing" : ["Availability Testing",
    #                                 "Failure Tolerance Testing",
    #                                 "Fault Tolerance Testing"],
    #     "Recovery Performance Testing" : ["Performance-related Testing",
    #                                       "Recoverability Testing"],
    #     "Transfer Recovery Testing" : ["Recoverability Testing"],
    # },
    remove = {
        "Scalability Testing" : [(SYN, "Capacity Testing"),
                                 (SYN, "Elasticity Testing")],
    }
)

performanceGraph = CustomGraph(
    "performance",
    {"Availability Testing", "Backup and Recovery Testing",
     "Backup/Recovery Testing", "Capacity Testing", "Concurrency Testing",
     "Disaster/Recovery Testing", "Efficiency Testing", "Elasticity Testing",
     "Endurance Testing", "Failover Testing", "Failover/Recovery Testing",
     "Failure Tolerance Testing", "Fault Tolerance Testing", "Load Testing",
     "Memory Management Testing", "Performance Efficiency Testing",
     "Performance Testing", "Performance-related Testing", "Power Testing",
     "Recoverability Testing", "Recovery Performance Testing",
     "Recovery Testing", "Reliability Testing", "Resource Utilization Testing",
     "Response-Time Testing", "Scalability Testing", "Soak Testing",
     "Stress Testing", "Transaction Flow Testing", "Usability Testing",
     "Volume Testing"},
    add = {
        "Capacity Testing" : ["Load Testing"],
        "Concurrency Testing" : ["Performance-related Testing"],
        "Performance Testing" : ["Load Testing"],
        "Reliability Testing" : ["Performance-related Testing"],
    },
    remove = {
        "Capacity Testing" : [(SYN, "Scalability Testing"),
                              "Performance Testing"],
        "Concurrency Testing" : ["Performance Testing"],
        "Load Testing" : ["Capacity Testing", "Performance Testing"],
        "Performance Testing" : [(SYN, "Performance-related Testing"),
                                 "Performance Testing"],
        "Performance Efficiency Testing" : ["Performance Testing"],
        "Reliability Testing" : ["Performance Testing"],
        "Response-Time Testing" : ["Performance Testing"],
        "Scalability Testing" : ["Elasticity Testing"],
        "Soak Testing" : True,
        "Stress Testing" : ["Performance Testing"],
        "Usability Testing" : ["Usability Testing"],
    }
)

performanceGraph.inherit(recoveryGraph)
performanceGraph.inherit(scalabilityGraph)

if "Example" not in csvFilename:
    for subgraph in {subsumesGraph, specBasedGraph, recoveryGraph,
                     scalabilityGraph, performanceGraph}:
        subgraph.buildGraph()
