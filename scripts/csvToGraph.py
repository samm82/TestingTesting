from pandas import read_csv
import re

approaches = read_csv('ApproachGlossary.csv')
names = approaches["Name"].to_list()
parents = approaches["Parent(s)"].to_list()

def removeInParens(s):
    # Remove nested parentheses first, if they exist
    s = re.sub(r" \(.*\(.*\).*\)", "", s)
    s = re.sub(r" \(.*\(.*\)\)", "", s)
    return re.sub(r" \(.*?\)", "", s)

def lineBreak(s):
    return f"<{s.replace(" ", "<br/>")}>"

def formatApproach(s):
    for c in "?-/() ":
        s = s.replace(c, "")
    s = s = s.replace("0", "Zero")
    s = s = s.replace("1", "One")
    s = s = s.replace(" (Testing)", " Testing")
    return removeInParens(s)

names = [removeInParens(n) for n in names if type(n) is str]

parents = [removeInParens(p).split(", ")
           if type(p) is str else [] for p in parents]

dot = [
    "\\documentclass{article}",
    "\\usepackage{graphicx}",
    "\\usepackage[pdf]{graphviz}",
    "\\usepackage{tikz}",
    "\\usetikzlibrary{arrows,shapes}",
    "",
    "\\begin{document}",
    "\\digraph{approachGraph}{",
    "rankdir=BT;",
    "",
]

for name in names:
    dashed = False
    if "?" in name:
        name = name.replace("?", "")
        dashed = True
    dot.append(f"{formatApproach(name)} [label={lineBreak(name)}{",style=dashed" if dashed else ""}];")

dot.append("")

for name, parent in zip(names, parents):
    for p in parent:
        dashed = False
        if "?" in p:
            dashed = True
        dot.append(f"{formatApproach(name).replace(" ", "")} -> {formatApproach(p)}{"[style=dashed]" if dashed else ""};")

dot += [
    "}",
    "\\end{document}",
]

with open("assets/graphs/approachGraph.tex", "w") as outFile:
    outFile.writelines(line + '\n' for line in dot)