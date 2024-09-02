import re

from helpers import *

SECTIONS = ["Std", "Meta", "Text", "Other"]
SEVERITIES = {"high": "Medium", "med": "Low", "low": ""}

class DiscrepSection:
    def __init__(self, filename: str):
        self.filename = filename
        for severity in SEVERITIES.keys():
            setattr(self, severity, 0)

sections = {x: DiscrepSection(f"chapters/05{chr(97+i)}_{x.lower()}_discreps.tex")
    for i, x in enumerate(SECTIONS)}

# Default value is one, for overriding counts
def update_section(sec, sev, contents: str ="\n\\item"):
    setattr(sections[sec], sev, getattr(sections[sec], sev) +
            len(re.findall(r"\n\s{0,12}\\item", contents)))

def override_severities(contents):
    for sev, secs in re.findall(r"% Severity: (\w+) \(([\w, ]+)\)", contents):
        for sec in secs.split(", "):
            update_section(sec, sev.lower())

override_severities(readFileAsStr("chapters/05_discrepancies.tex"))

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
writeFile([f"{getattr(sections[sec], sev)}% {sev.capitalize()} {sec} Discrepancies"
           for sec in SECTIONS for sev in SEVERITIES.keys()] +
           [f"{total}% Total Other Discrepancies"], "otherDiscrepCounts", True)
