from pandas import read_csv
import re

approaches = read_csv('ApproachGlossary.csv')
names = approaches["Name"].to_list()
parents = approaches["Parent(s)"].to_list()

def removeInParens(s):
    return re.sub(r" \(.*?\)", "", s)

def lineBreak(s):
    return f"<{s.replace(" ", "<br/>")}>"

names = [lineBreak(removeInParens(n)) for n in names if type(n) is str]

parents = [list(map(lineBreak, removeInParens(p).split(", ")))
           if type(p) is str else [""] for p in parents]

for name, parent in zip(names, parents):
    if ";" in "".join(parent):
        print(name, "".join(parent))
