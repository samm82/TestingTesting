import numpy as np
from pandas import read_csv
import re

approaches = read_csv('ApproachGlossary.csv')
names = approaches["Name"].to_list()
categories = approaches["Approach Category"].to_list()
synonyms = approaches["Synonym(s)"].to_list()
parents = approaches["Parent(s)"].to_list()

def processCol(col):
    col = [re.split(r',(?!(?:[^()]*\([^()]*\))*[^()]*\)) ', x)
            if type(x) is str else [] for x in col]
    for x in col:
        for i in range(len(x)-1, 1, -1):
            if "(" in x[i] and "(" not in x[i-1] and not x[i].startswith("("):
                x[i-1] = f"{x[i-1]} ({x[i].split(" (", 1)[1]}"
    return col

names = [n for n in names if type(n) is str]
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

def isUnsure(name):
    return any(unsure in name for unsure in
               {"?", "(implied", "(inferred", "(can be",
                "(usually", "(if" , " (Testing)"})

def addLineToCategory(key, line):
    if line not in categoryDict[key][1] and "-> ;" not in line:
        categoryDict[key][1].append(line)

def removeInParens(s):
    s = s.replace(" (Testing)", " Testing")
    # s = re.sub(r" \(.*?\) \(.*?\)", "", s)
    # Remove nested parentheses first, if they exist
    s = re.sub(r" \([^\)]*\([^\)]*\)[^\)]*\)", "", s)
    s = re.sub(r"\([^\)]*\([^\)]*\)[^\)]*\)", "", s)
    s = re.sub(r" \(.*?\)", "", s)
    if "(" not in s:
        s = s.strip(")")
    return s.replace("?", "")

def lineBreak(s):
    return f"<{s.replace(" ", "<br/>")}>"

def formatApproach(s):
    s = removeInParens(s)
    for c in "?-/() ":
        s = s.replace(c, "")
    s = s.replace("0", "Zero")
    s = s.replace("1", "One")
    return s.strip(",")

def addNode(name, style = "", key = "Approach"):
    dashed = isUnsure(name)
    if dashed:
        name = name.replace("?", "")
    name = removeInParens(name)

    extras = [f"label={lineBreak(name)}"]
    styles = [s for s in ["dashed" if dashed else "", style] if s]
    if styles:
        extras.append(f'style="{",".join(styles)}"')
    nameLine = f"{formatApproach(name)} [{",".join(extras)}];"

    for k in staticKeywords:
        if k in name and name not in dynamicExceptions:
            categoryDict["Static"][0].append(removeInParens(name))
            staticApproaches.add(formatApproach(name))
            break
    
    if style == "filled" and key == "Static":
        addLineToCategory("Static", nameLine)
        return

    if formatApproach(name) in staticApproaches:
        addLineToCategory("Static", nameLine)
    addLineToCategory(key, nameLine)

for name, category in zip(names, categories):
    if type(category) is str:
        for key in categoryDict.keys():
            if key in category or key == "Approach":
                categoryDict[key][0].append(removeInParens(name))
                addNode(name, key=key)

        # # For finding categorization discrepancies
        # split_cat = [c for c in removeInParens(category).split(", ")
        #              if c.startswith(('Level', 'Practice', 'Technique', 'Type'))
        #                 and f"{c} (implied" not in category and f"{c} (inferred" not in category
        #                 and not c.endswith('?')]
        # if len(split_cat) > 1:
        #     print(name)
        #     print(f"{name.capitalize()} is categorized as both a test {\
        #         split_cat[0].lower()} and a test {split_cat[1].lower()}")
        #     print("\t", category)

for key in categoryDict.keys():
    categoryDict[key][1].append("")

def addToIterable(s, iterable, key=key):
    if type(iterable) is list:
        if removeInParens(s) not in iterable:
            addNode(s, style="dotted", key=key)
            iterable.append(removeInParens(s))
    elif type(iterable) is set:
        if formatApproach(s) not in iterable:
            addNode(s, style="filled", key=key)
            iterable.add(formatApproach(s))
    else:
        raise ValueError(f"addToIterable unimplemented for {type(
            iterable)}")

# Add synonym relations
synDict, nameDict = {}, {}
synSets = {}
for name, synonym in zip(names, synonyms):
    for syn in synonym:
        if not ("spelled" in syn.lower() or "called" in syn.lower() or
                formatApproach(syn).isupper()):
            try:
                synDict[removeInParens(syn)].append(removeInParens(name))
            except KeyError:
                synDict[removeInParens(syn)] = [removeInParens(name)]
            try:
                nameDict[removeInParens(name)].append(removeInParens(syn))
            except KeyError:
                nameDict[removeInParens(name)] = [removeInParens(syn)]
            # To only track relation one way and check inconsistencies
            try:
                if synSets[f"{formatApproach(name)}->{formatApproach(syn)}"] != isUnsure(syn):
                    raise ValueError(f"Mismatch between rigidity of synonyms {formatApproach(
                        syn)} and {formatApproach(name)}")
            except KeyError:
                synSets[f"{formatApproach(syn)}->{formatApproach(name)}"] = isUnsure(syn)

for key in categoryDict.keys():
    for syn, terms in synDict.items():
        terms = [x for x in terms
                 if removeInParens(x) in categoryDict[key][0]]
        if (removeInParens(syn) in categoryDict[key][0] or
                (len(terms) > 1)):
            validTerms = [term for term in terms if f"{formatApproach(
                syn)}->{formatApproach(term)}" in synSets.keys()]
            if validTerms:
                addToIterable(syn, categoryDict[key][0], key)
                for term in validTerms:
                    addToIterable(term, categoryDict[key][0], key)
                    addLineToCategory(
                        key, f"{formatApproach(
                            term)} -> {formatApproach(
                                syn)}[dir=none{',style="dashed"' if synSets[f"{formatApproach(
                                    syn)}->{formatApproach(term)}"] else ""}];")
    if categoryDict[key][1][-1] != "":
        categoryDict[key][1].append("")

    # ONLY USE SAME RANK FOR THESE CATEGORIES
    if key in {}:
        nameDict.update(synDict)
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

workingStaticSet = staticApproaches.copy()

# Add parent relations
for name, parent in zip(names, parents):
    # if [x for x in parent + [name] if "keyword" in x.lower()]:
    for par in parent:
        fpar = formatApproach(par)
        if not fpar:
            continue

        fname = formatApproach(name)
        parentLine = f"{fname} -> {fpar}{'[style="dashed"]'
                                         if isUnsure(par) else ""};"

        for key in categoryDict.keys():
            if key == "Static" and (fname in staticApproaches or
                                    fpar in staticApproaches):
                addToIterable(name, workingStaticSet, "Static")
                addToIterable(par, workingStaticSet, "Static")
                addLineToCategory("Static", parentLine)
            elif (removeInParens(name) in categoryDict[key][0] and
                removeInParens(par) in categoryDict[key][0]):
                addLineToCategory(key, parentLine)

def splitListAtEmpty(listToSplit):
    recArr = np.array(listToSplit)
    return [subarray.tolist() for subarray in
            np.split(recArr, np.where(recArr == "")[0]+1)
            if len(subarray) > 0]

def styleInLine(style, line):
        return re.search(r"label=.+,style=.+" + style, line)

def make_dot_file(lines, filename):
    LONG_EDGE_LABEL = 'label="                "'

    syns = [line.split(" ")[0] for line in lines if styleInLine("dotted", line)]
    synsToRemove = [syn for syn in syns if sum(1 for line in lines if syn in line) < 3]
    lines = [line for line in lines if not any(syn in line for syn in synsToRemove)]

    impTerm, dynTerm = '', ''
    if any(styleInLine("dashed", line) for line in lines):
        impTerm = 'imp5 [label=<Implied<br/>Term> style="dashed"]'

    if any(styleInLine("filled", line) for line in lines):
        dynTerm = 'dyn [label=<Dynamic<br/>Approach> style="filled"]'

    twoSyn = [
        'syn3 [label=<Term>]',
        'syn4 [label=<Synonym<br/>to Both> style="dotted"]',
        'syn5 [label=<Term>]',
        'syn3 -> syn4 -> syn5 [dir=none]',
    ] if len(syns) > len(synsToRemove) else []
    
    def sameRank(lines):
        return ['{', 'rank=same'] + lines + ['}']

    def impOrDynWithSyn(nodes, forceDyn=False):
        if len(nodes) == 1:
            nodes = nodes[0]
        else:
            nodes = f'{{ {" ".join(nodes)} }}'
        return f'{'imp5' if impTerm and not forceDyn else 'dyn'} -> {nodes}'

    def twoSynAlign(nodes):
        synNodes = [f'syn{i}' for i in range(3, 6, 2 if len(nodes) == 2 else 1)]
        for i in range(len(synNodes)):
            synNodes[i] = f'{synNodes[i]} -> {nodes[i]}'
        return synNodes

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

    # From https://stackoverflow.com/a/65443720/10002168
    legend = [
        '',
        'subgraph cluster_legend {',
        '    label="Legend";',
        # This puts the label at the top, not the bottom, because of the rankdir
        '    labelloc="b";',
        '    fontsize="48pt"',
        '    rankdir=BT',
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
    ] + extras + [
        # For alignment
        '    edge [style="invis"]',
        '    imp1 -> chd',
        '    imp2 -> par',
        '    imp3 -> syn1',
        '    imp4 -> syn2',
    ] + align + [
        '}',
        '',
        '// Connect the dummy node to the first node of the legend',
        'start -> chd [style="invis"];',
    ]
    lines = [
        "\\documentclass{article}",
        "\\usepackage{graphicx}",
        "\\usepackage[pdf]{graphviz}",
        "\\usepackage{tikz}",
        "\\usetikzlibrary{arrows,shapes}",
        "",
        "\\begin{document}",
        f"\\digraph{{{filename}}}{{",
        "rankdir=BT;",
        '',
        '// Dummy node to push the legend to the top left',
        'start [style="invis"];',
        "",
    ] + lines + legend + [
        "}",
        "\\end{document}",
    ]

    with open(f"assets/graphs/{filename}.tex", "w") as outFile:
        outFile.writelines(line + '\n' for line in lines)

for key, value in categoryDict.items():
    lines = value[1]
    make_dot_file(lines, f"{key.lower()}Graph")
    unsure = ["dashed"] + [c.split()[0] for c in lines if styleInLine("dashed", c)]
    make_dot_file([c for c in lines if all(x not in c for x in unsure)],
                  f"rigid{key}Graph")

recoveryTerms = ["AvailabilityTesting", "BackupandRecoveryTesting", "BackupRecoveryTesting",
                 "DisasterRecoveryTesting", "FailoverTesting", "FailoverRecoveryTesting",
                 "FailureToleranceTesting", "FaultToleranceTesting", "PerformanceTesting",
                 "PerformancerelatedTesting", "RecoverabilityTesting", "RecoveryTesting",
                 "ReliabilityTesting", "UsabilityTesting"]
# Optimized with ChatGPT to remove redundant checks and extra new lines
recoveryLines = [line for line in categoryDict["Approach"][1]
                 if any(term in line for term in recoveryTerms) or line == ""]

chunks = splitListAtEmpty(categoryDict["Approach"][1])
if len(chunks) == 3:
    nodes = chunks[0] + chunks[1]
    rels = chunks[1] + chunks[2]
elif len(chunks) == 4:
    nodes = chunks[0] + chunks[1]
    rels = chunks[1] + chunks[2] + chunks[3]
else:
    raise ValueError("Unexpected grouping of lines for automatic recovery graph")

rels = [line for line in rels if line == "" or
        (line.split(" -> ")[0] in recoveryTerms and
         line.split(" -> ")[1].split("[")[0].strip(";") in recoveryTerms) or
        (line.split(" ")[1] in recoveryTerms and
         line.split(" ")[2].strip("}") in recoveryTerms)]
nodes = [node for node in nodes if "->" not in node and
         any(node.split(" ")[0] in line for line in rels)]

make_dot_file(nodes+rels, "recoveryGraph")

# print(staticApproaches)