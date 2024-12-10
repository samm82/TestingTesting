from pandas import read_csv
import sys

from helpers import writeFile

if len(sys.argv) < 2 or sys.argv[1].lower() not in {"y", "n"}:
    sys.exit("Unexpected value of UNDEF. Are you researching an undefined term? (y/n)")

approaches = read_csv('ApproachGlossary.csv')

def readInt(f) -> int:
    return int(f.readline().strip())

with open("assets/misc/undefTermCounts.tex", "r",
          encoding="utf-8") as readFile:
    totalBefore = readInt(readFile)
    undefBefore = readInt(readFile)
    totalAfter  = readInt(readFile)
    undefAfter  = readInt(readFile)

print([totalBefore, undefBefore, totalAfter, undefAfter])

newTotalAfter = len(approaches)
newUndefAfter = approaches["Definition"].isna().sum()

if sys.argv[1].lower() == "n":
    # "Before" counts should increase with "after" counts UNLESS they are being investigated
    totalBefore += (newTotalAfter - totalAfter)
    undefBefore += (newUndefAfter - undefAfter)
# These get updated regardless
totalAfter = newTotalAfter
undefAfter = newUndefAfter

# Populate values for Undefined Terms section
writeFile([totalBefore, undefBefore, totalAfter, undefAfter],
          "undefTermCounts", dir="misc")