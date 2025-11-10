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
# Omit inaccessible source mentioned for traceability flaw
sources.discard("MusaEtAl1987")
# Reintroduce ISTQB because of how it is formatted for citations
sources.discard("")
sources.add("ISTQB2024")
# Omit internal paper references
sources = {s for s in sources if not s.startswith(tuple(INTERNAL_REFS))}

# Based on ChatGPT
def sort_key(s: str, cat: SrcCat) -> tuple:
    match = re.search(r'(\d+)', s)
    year = -int(match.group())
    end = s[match.end():]
    start = s[:match.start()]
    if cat == SrcCat.STD:
        # Second IEEE for sources without ISO/IEC
        start = ["IEEE", "ISO_IEC", "ISO", "IEEE"].index(start)
        if not start and str(-year) in ONLY_IEEE:
            start = 3
        return (start, year, end)
    authCount = 0
    for i, multiAuth in enumerate(["And", "EtAl"], start=1):
        if multiAuth in s:
            authCount = -i
    return (year, authCount, start, end)

unknownSpaces = {s for s in sources if " " in s and s not in
                # List of sources with spaces that can be parsed by just removing them
                {"Mackert GmbH2022", "Kuan Tan2008", "KanewalaAndYueh Chen2019"}}
if unknownSpaces:
    print("Sources with spaces to double check: ")
    for s in unknownSpaces:
        print("\t" + s)
    input()
else:
    for cat in SrcCat:
        catSources = sorted({s.replace(' ', '') for s in sources if getSrcCat(s) == cat},
                            key=lambda s: sort_key(s, cat))
        catSourceLine = f"\\citep{{{','.join(catSources)}}}"
        if cat == SrcCat.META:
            # Handle edge cases; this might not be stable
            catSourceLine = ("(\\citealp{SWEBOK2025,SWEBOK2024}; \\citealpISTQB{}; \\citealp{" +
                                ','.join([s for s in catSources if s not in 
                                          {"SWEBOK2025", "SWEBOK2024", "ISTQB2024"}]) + "})")
        writeFile([cat.longname, catSourceLine, len(catSources)],
                  f"{cat.name.lower()}Sources", True)
