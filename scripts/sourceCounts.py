from pandas import read_csv
import re
import sys

from discrepCounter import SrcCat, getSrcCat
from helpers import *

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sourceCounts.py <filenames>")
        sys.exit(1)

sources = set()
for filename in sys.argv[1:]:
    for _, row in read_csv(filename).iterrows():
        for cell in row.to_list():
            for word in {"See", "OG", "FIND"}:
                cell = str(cell).split(word+" ")[0]
        sources.update(s[1:-1].replace(" and ", "And") for s in re.findall(
            r"\{.*?\}", formatLineWithSources(parseSource(cell), False)))
# Omit private communication as a source; used for notes
sources.discard("SmithAndCarette2023")
# Reintroduce ISTQB because of how it is formatted for citations
sources.discard("")
sources.add("ISTQB2024")

# Based on ChatGPT
def sort_key(s):
    match = re.search(r'(\d+)', s)
    return (-int(match.group()), s[match.end():], s[:match.start()])

unknownSpaces = {s for s in sources if " " in s and s not in
                # List of sources with spaces that can be parsed by just removing them
                {"Mackert GmbH2022", "Kuan Tan2008"}}
if unknownSpaces:
    print("Sources with spaces to double check: ")
    for s in unknownSpaces:
        print("\t" + s)
    print()
else:
    for cat in SrcCat:
        catSources = sorted({s.replace(' ', '') for s in sources if getSrcCat(s) == cat},
                            key=sort_key)
        catSourceLine = f"\\citep{{{','.join(catSources).replace("ISTQB2024", "ISTQB")}}}"
        if cat == SrcCat.META:
            # Handle edge case of ISTQB; this might not be stable
            catSourceLine = ("\\ifnotpaper \\citetext{\\citealpISTQB{}; \\citealp{" +
                                ','.join([s for s in catSources if not s.startswith("ISTQB")]) +
                                "}} \\else " + catSourceLine + " \\fi")
        writeFile([cat.longname, catSourceLine,
                    str(len(catSources))], f"{cat.name.lower()}Sources", True)