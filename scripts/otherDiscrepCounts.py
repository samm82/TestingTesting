import re

from flawCounter import SrcCat
from helpers import *

SECTIONS = [k.name.capitalize() for k in SrcCat if k.color.value >= 0]
SEVERITIES = {"high": "Medium", "med": "Low", "low": ""}

class FlawSection:
    def __init__(self, filename: str):
        self.filename = filename
        for severity in SEVERITIES.keys():
            setattr(self, severity, 0)

sections = {x: FlawSection(f"chapters/05{chr(97+i)}_{x.lower()}_flaws.tex")
    for i, x in enumerate(SECTIONS)}

# Default value is one, for overriding counts
def update_section(sec, sev, contents: str ="\n\\item"):
    setattr(sections[sec], sev, getattr(sections[sec], sev) +
            len(re.findall(r"\n\s{0,12}\\item", contents)) -
            # Count all flaws except those that are categorized
            len(re.findall(r"\\item % Flaw count \([A-Z]+(?<!OTHER)\):", contents)))

def override_severities(contents):
    for sev, secs in re.findall(r"% Severity: (\w+) \(([\w, ]+)\)", contents):
        for sec in secs.split(", "):
            update_section(sec, sev.lower())

override_severities(readFileAsStr("chapters/05_flaws.tex"))

for name, s in sections.items():
    contents = readFileAsStr(s.filename)
    override_severities(contents)

    for severity, splitVal in SEVERITIES.items():
        if splitVal:
            splitVal = splitVal + " Severity"
            if contents.count(splitVal) > 1:
                raise ValueError(f"More than one '{splitVal}' found in {name}")
            sevContents, contents = contents.split(splitVal)
            update_section(name, severity, sevContents)
        else:
            update_section(name, severity, contents)

total = sum(getattr(sections[sec], sev) for sec in SECTIONS for sev in SEVERITIES.keys())
writeFile([f"{getattr(sections[sec], sev)}% {sev.capitalize()} {sec} Flaws"
           for sec in SECTIONS for sev in SEVERITIES.keys()] +
           [f"{total}% Total Other Flaws"], "otherFlawCounts", True)
