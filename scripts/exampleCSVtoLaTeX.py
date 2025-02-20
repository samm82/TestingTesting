from pandas import read_csv

from helpers import writeTblr

class ExGloss:
    def __init__(self, name: str, rel: str, relsRef: str, head: list[str]):
        self.filename = name
        self.caption = ("Example glossary entries demonstrating how we track "
                        f"{rel} relations (see \\Cref{{{relsRef}}}).")
        _mainHeader = f"{head}(s)"
        self.headers = ["Name\\TblrNote{a}", _mainHeader]

        _lines = read_csv("assets/graphs/exampleGlossaries/"
                         f"{self.filename[0].upper()}{self.filename[1:]}.csv")
        self.lines = [f"{name} & {"" if isinstance(col, float) else col} \\\\"
                      for name, col in zip(
                          _lines["Name"].to_list(),
                          _lines[_mainHeader].to_list())]

        self.env = "talltblr"
        self.widths = [0.4, 0.6]
        self.footnotes = ["``Name'' can refer to the name of a test approach, "
            "software quality, or other testing-related term, but we only "
            "generate graphs for test approaches."]
        self.xCol = False
        self.toSort = False
        self.rowDataSpec: str = "c"

exGlosses = [
    ExGloss("exampleGlossary",    "parent-child", "par-chd-rels", "Parent"),
    ExGloss("synExampleGlossary", "synonym",      "syn-rels",     "Synonym")
]

for exGloss in exGlosses:
    writeTblr(**exGloss.__dict__)
