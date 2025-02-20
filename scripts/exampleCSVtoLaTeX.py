from helpers import writeTblr

class ExGloss:
    def __init__(self, name: str, rel: str, relsRef: str,
                 head: list[str], lines: list[str]):
        self.filename = name
        self.caption = ("Example glossary entries demonstrating how we track "
                        f"{rel} relations (see \\Cref{{{relsRef}}}).")
        self.headers = ["Name\\TblrNote{a}", f"{head}(s)"]
        self.lines = lines
        self.env = "talltblr"
        self.widths = [0.4, 0.6]
        self.footnotes = ["``Name'' can refer to the name of a test approach, "
            "software quality, or other testing-related term, but we only "
            "generate graphs for test approaches."]
        self.xCol = False
        self.toSort = False
        self.rowDataSpec: str = "c"

exGlosses = [
    ExGloss("exampleGlossary", "parent-child", "par-chd-rels", "Parent", [
        "A                           & B (Author, 0000; 0001), C (0000) \\\\",
        "B                           & C (implied by Author, 0000)      \\\\",
        "C                           & D (Author, 0002)                 \\\\",
        "D (implied by Author, 0002) &                                  \\\\"
    ]),
    ExGloss("synExampleGlossary", "synonym", "syn-rels", "Synonym", [
        "E                        & F (Author, 0000; implied by 0001)     \\\\",
        "G                        & F (Author, 0002), H (implied by 0000) \\\\",
        "H                        & X                                     \\\\"
    ])
]

for exGloss in exGlosses:
    writeTblr(**exGloss.__dict__)
