from pandas import read_csv
import re

approaches = read_csv('ApproachGlossary.csv')
names = approaches["Name"].to_list()
categories = approaches["Approach Category"].to_list()
parents = approaches["Parent(s)"].to_list()

def removeInParens(s):
    # s = re.sub(r" \(.*?\) \(.*?\)", "", s)
    # Remove nested parentheses first, if they exist
    s = re.sub(r" \([^\)]*\([^\)]*\)[^\)]*\)", "", s)
    s = re.sub(r"\([^\)]*\([^\)]*\)[^\)]*\)", "", s)
    return re.sub(r" \(.*?\)", "", s)

def lineBreak(s):
    return f"<{s.replace(" ", "<br/>")}>"

def formatApproach(s):
    s = s.replace(" (Testing)", " Testing")
    for c in "?-/() ":
        s = s.replace(c, "")
    s = s.replace("0", "Zero")
    s = s.replace("1", "One")
    return removeInParens(s).strip(",")

names   = [n for n in names if type(n) is str]
parents = [re.split(r',(?!(?:[^()]*\([^()]*\))*[^()]*\)) ', par)
            if type(par) is str else [] for par in parents]
for par in parents:
    for i in range(len(par)-1, 1, -1):
        if "(" in par[i] and "(" not in par[i-1] and not par[i].startswith("("):
            par[i-1] = f"{par[i-1]} ({par[i].split(" (", 1)[1]}"

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
    return any(unsure in name for unsure in {"?", "(implied", "(inferred", "(can be", "(usually"})

def addNode(name, filled = False, key = "Approach"):
    dashed = False
    if isUnsure(name):
        name = name.replace("?", "")
        dashed = True
    name = removeInParens(name).strip(")")
    extra = [
        f"label={lineBreak(name)}",
        f'style="{",".join([
            s for s in ["dashed" if dashed else "",
                        "filled" if filled else ""] if s
            ])}"' if dashed or filled else ""
    ]
    nameLine = f"{formatApproach(name)} [{",".join([e for e in extra if e])}];"

    for k in staticKeywords:
        if k in name and name not in dynamicExceptions:
            staticApproaches.add(formatApproach(name))
            break
    
    if filled and key == "Static":
        categoryDict["Static"][1].append(nameLine)
        return

    if formatApproach(name) in staticApproaches:
        categoryDict["Static"][1].append(nameLine)
    categoryDict[key][1].append(nameLine)

for name, category in zip(names, categories):
    addNode(name)
    if type(category) is str:
        for key in categoryDict.keys():
            if key in category:
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

workingStaticSet = staticApproaches.copy()

for name, parent in zip(names, parents):
    # if [x for x in parent + [name] if "keyword" in x.lower()]:
    for par in parent:
        if not par:
            continue
        dashed = False
        if isUnsure(name):
            dashed = True
        fname = formatApproach(removeInParens(name))
        fpar  = formatApproach(removeInParens(par))
        parentLine = f"{fname} -> {fpar}{"[style=dashed]" if dashed else ""};"
        if fname in staticApproaches or fpar in staticApproaches:
            if fname not in workingStaticSet:
                addNode(name, filled=True, key="Static")
                workingStaticSet.add(fname)
            elif fpar not in workingStaticSet:
                addNode(par, filled=True, key="Static")
                workingStaticSet.add(fpar)
            categoryDict["Static"][1].append(parentLine)
        else:
            categoryDict["Approach"][1].append(parentLine)
        
        for key in categoryDict.keys():
            if (removeInParens(name) in categoryDict[key][0] and
                removeInParens(par) in categoryDict[key][0]):
                categoryDict[key][1].append(parentLine)

def make_dot_file(lines, filename):
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
        "",
    ] + lines + [
        "}",
        "\\end{document}",
    ]

    with open(f"assets/graphs/{filename}.tex", "w") as outFile:
        outFile.writelines(line + '\n' for line in lines)

for key, value in categoryDict.items():
    lines = value[1]
    make_dot_file(lines, f"{key.lower()}Graph")
    unsure = ["dashed"] + [c.split()[0] for c in lines if '>,style="dashed"' in c]
    make_dot_file([c for c in lines if all(x not in c for x in unsure)],
                  f"rigid{key}Graph")

# print(staticApproaches)