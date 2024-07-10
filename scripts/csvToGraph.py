from pandas import read_csv
import re

approaches = read_csv('ApproachGlossary.csv')
names = approaches["Name"].to_list()
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
    for c in "?-/() ":
        s = s.replace(c, "")
    s = s.replace("0", "Zero")
    s = s.replace("1", "One")
    s = s.replace(" (Testing)", " Testing")
    return removeInParens(s).strip(",")

names = [removeInParens(n) for n in names if type(n) is str]

parents = [removeInParens(p).strip(",").split(", ")
           if type(p) is str else [] for p in parents]

dot, staticDot = [], []
staticApproaches = {
    'ConcreteExecution', 'SymbolicExecution', 'InductiveAssertionMethods',
    'ContentChecking', 'ModelVerification'}
staticKeywords = {'Audit', 'Inspection' 'Proof', 'Review', 'Static', 'Walkthrough'}
dynamicExceptions = {}

def addNode(name, staticOnly = False):
    dashed = False
    if "?" in name:
        name = name.replace("?", "")
        dashed = not staticOnly
    extra = [
        f"label={lineBreak(name.strip(")"))}",
        f'style="{",".join([
            s for s in ["dashed" if dashed else "",
                        "filled" if staticOnly else ""] if s
            ])}"' if dashed or staticOnly else ""
    ]
    nameLine = f"{formatApproach(name)} [{",".join([e for e in extra if e])}];"

    for k in staticKeywords:
        if k in name and name not in dynamicExceptions:
            staticApproaches.add(formatApproach(name))
            break
    
    if staticOnly:
        staticDot.append(nameLine)
        return

    if formatApproach(name) in staticApproaches:
        staticDot.append(nameLine)
    else:
        dot.append(nameLine)

for name in names:
    addNode(name)

dot.append("")
staticDot.append("")

workingStaticSet = staticApproaches.copy()

for name, parent in zip(names, parents):
    # if [x for x in parent + [name] if "keyword" in x.lower()]:
    for p in parent:
        if not p:
            continue
        dashed = False
        if "?" in p:
            dashed = True
        fname, fp = formatApproach(name), formatApproach(p)
        parentLine = f"{fname} -> {fp}{"[style=dashed]" if dashed else ""};"
        if fname in staticApproaches or fp in staticApproaches:
            if fname not in workingStaticSet:
                print("name", name)
                addNode(name, staticOnly=True)
                workingStaticSet.add(fname)
            elif fp not in workingStaticSet:
                print("p", p)
                addNode(p, staticOnly=True)
                workingStaticSet.add(fp)
            staticDot.append(parentLine)
        else:
            dot.append(parentLine)

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

make_dot_file(dot, "approachGraph")
make_dot_file(staticDot, "staticGraph")

print(staticApproaches)