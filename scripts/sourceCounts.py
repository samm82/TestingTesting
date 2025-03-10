from pandas import read_csv
import re
import sys

from flawCounter import SrcCat, getSrcCat, TEX_FILES
from helpers import *

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sourceCounts.py <filenames>")
        sys.exit(1)

sources: set[str] = set()
for filename in sys.argv[1:]:
    for _, row in read_csv(filename).iterrows():
        for cell in row.to_list():
            cell = re.sub(r"See .*\d{4}.*", "", str(cell))
            for word in {"FIND", "OG"}:
                cell = re.sub(fr"{word} [^;]*?\)", ")", cell)
                cell = re.sub(fr"{word} [^\)]*?;", ";", cell)
            # Ignore manual references; e.g., \Cref{label}
            sources.update(re.findall(r"(?<!ref)\{(.*?)\}",
                                      formatLineWithSources(cell, False)))
for filename in TEX_FILES:
    with open(filename, "r", encoding="utf-8") as file:
        sources.update(re.findall(
            r"\{(.*?)\}", " ".join([line.split(":")[1]
                                  for line in file.readlines()
                                  if "% Flaw count" in line])))

# Omit private communication as a source; used for notes
sources.discard("SmithAndCarette2023")
# Reintroduce ISTQB because of how it is formatted for citations
sources.discard("")
sources.add("ISTQB2024")
# Omit internal paper references
sources = {s for s in sources if not s.startswith(tuple(INTERNAL_REFS))}

ONLY_IEEE = {"2012"}
# Based on ChatGPT
def sort_key(s: str, cat: SrcCat):
    match = re.search(r'(\d+)', s)
    year = -int(match.group())
    end = s[match.end():]
    start = s[:match.start()]
    if cat == SrcCat.STD:
        # Second IEEE for sources without ISO/IEC
        start = ["IEEE", "IEEE", "ISO_IEC", "ISO"].index(start)
        if not start and str(-year) in ONLY_IEEE:
            start = 1
    return (start, year, end)

unknownSpaces = {s for s in sources if " " in s and s not in
                # List of sources with spaces that can be parsed by just removing them
                {"Mackert GmbH2022", "Kuan Tan2008", "KanewalaAndYueh Chen2019"}}
if unknownSpaces:
    print("Sources with spaces to double check: ")
    for s in unknownSpaces:
        print("\t" + s)
    print()
else:
    for cat in SrcCat:
        catSources = sorted({s.replace(' ', '') for s in sources if getSrcCat(s) == cat},
                            key=lambda s: sort_key(s, cat))
        catSourceLine = f"\\citealp{{{','.join(catSources).replace("ISTQB2024", "ISTQB")}}}"
        if cat == SrcCat.META:
            # Handle edge case of ISTQB; this might not be stable
            catSourceLine = ("\\ifnotpaper \\citealpISTQB{}; \\citealp{" +
                                ','.join([s for s in catSources if not s.startswith("ISTQB")]) +
                                "}\\else " + catSourceLine + "\\fi")
        writeFile([cat.longname, catSourceLine, len(catSources)],
                  f"{cat.name.lower()}Sources", True)
