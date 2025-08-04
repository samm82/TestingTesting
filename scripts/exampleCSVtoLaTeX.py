from pandas import read_csv

from helpers import capFirst, writeTblr

class ExGloss:
    def __init__(self, name: str, rel: str, relsRef: str, widths: list[float],
                 envArg: str = "hbtp!"):
        self.filename = name
        self.caption = ("Example glossary entries demonstrating how we track "
                        f"{rel} \\\\ relations (defined in \\Cref{{{relsRef}}}).")

        _mainHeader = f"{capFirst(rel.split("-")[0])}(s)"
        self.headers = ["Name\\TblrNote{a}", _mainHeader]

        _lines = read_csv("assets/graphs/exampleGlossaries/"
                          f"{capFirst(self.filename)}.csv")
        self.lines = [f"{name} & {"" if isinstance(col, float) else col} \\\\"
                      for name, col in zip(
                          _lines["Name"].to_list(),
                          _lines[_mainHeader].to_list())]

        self.env = "talltblr"
        self.envArg = envArg
        self.widths = widths
        self.footnotes = ["``Name'' can refer to the name of a test approach, "
            "software quality, or other testing-related term, but we only "
            "visualize relations between test approaches."]
        self.xCol = False
        self.toSort = False
        self.rowDataSpec: str = "c"

exGlosses = [
    ExGloss("exampleGlossary",    "parent-child", "par-chd-rels", [0.4,  0.6] , "bt!"),
    ExGloss("synExampleGlossary", "synonym",      "syn-rels"    , [0.25, 0.75], "bt!")
]

for exGloss in exGlosses:
    writeTblr(**exGloss.__dict__)
