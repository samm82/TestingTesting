from re import sub

from helpers import capFirst, wrapEnv, writeFile

# See #209
def footnoteHelper(label):
    return f"\\footnote{{Defined in \\Cref{{{label}}}.}}"

# CAT_FOOTNOTE = "\n\t".join([
#     "\\footnote{"
#     "A single test approach with more than one category ",
#     "\\ifnotpaper (for example, A/B Testing in \\Cref{tab:approachGlossaryExcerpt}) \\fi ",
#     "often indicates an underlying flaw; see \\Cref{multiCats}.} \n"])
# toRecord: list[str] = [
#     "names", f"categories{CAT_FOOTNOTE}(\\Cref{{cats-def}})",
#     "definitions", "synonyms (\\Cref{syn-rels})",
#     "parents (\\Cref{par-chd-rels})",
#     "flaws\\phantomsection{}\\label{manual-flaws} (\\Cref{flaw-def}) (in a separate document)"]

toRecord: list[str] = [
    "names", f"categories{footnoteHelper("cats-def")}",
    "definitions", f"synonyms{footnoteHelper("syn-rels")}",
    f"parents{footnoteHelper("par-chd-rels")}",
    f"flaws{footnoteHelper("flaw-def")}\\phantomsection{{}}\\label{{manual-flaws}}"
    " \\ifnotpaper (\\Cref{record-flaws})\\fi"]

# relatedTerms: list[str] = [
#     "imply related test approaches (\\Cref{derived-tests})",
#     "are used repeatedly",
#     "have complex definitions"
# ]
# """
# \\item \\phantomsection{}\\label{step:record-info}
# Alongside step~\\ref{step:ident-terms}, identifying and recording related
# testing terms that are used repeatedly and/or have complex definitions""" + "\n".join([
#     f"\t\t  {line}" for line in wrapEnv(
#         "enumerate", [f"\t\\item {capFirst(i)}" for i in relatedTerms])
#         ])

OTHER_NOTES = "other relevant notes"
OTHER_NOTES_EXS = ", ".join(["prerequisites", "uncertainties",
                             "other sources"])

methodology = ("""
    \\item \\phantomsection{}\\label{step:ident-sources}
          Identify authoritative sources \\ifnotpaper on software testing
          and ``snowball'' from them \\fi (\\Cref{ident-sources})
    \\item \\phantomsection{}\\label{step:ident-terms}
          Identify all test approaches""" + footnoteHelper("approach-def") +
          """ and testing-related terms (\\Cref{ident-terms}) described in
          these authoritative sources 
    \\item \\phantomsection{}\\label{step:record-info}
          Record all relevant data (\\Cref{record-info}), including
          implicit data (\\Cref{imp-info}), for each term identified in
          step~\\ref{step:ident-terms}; test approach data are comprised of:
          \n""" + "\n".join([
        f"\t\t  {line}" for line in wrapEnv(
            "enumerate", [f"\t\\item {capFirst(i)}"
                          for i in toRecord + [OTHER_NOTES +
                                               f" ({OTHER_NOTES_EXS}, etc.)"]])
        ]) + """
    \\item \\phantomsection{}\\label{step:repeat-process}
          Repeat steps~\\ref{step:ident-sources} to \\ref{step:record-info} for 
          any missing or unclear terms (\\Cref{undef-terms}) until the stopping
          criteria (\\Cref{stop-crit}) is reached""")
    
# Base methodology overview
writeFile(wrapEnv("enumerate", [methodology]), "methodOverviewList", helper=True)

toRecord[-1] = "and " + toRecord[-1]

for sec, verb in [("Intro", "start"), ("Conc", "do this")]:
    if sec == "Conc":
        toRecord = [sub(r"\\footnote\{Defined in .+\.\}", "", line)
                    for line in toRecord]
    methodOverview = [
        f"We {verb} by documenting the \\approachCount{{}} test approaches mentioned ",
        "by \\srcCount{} sources (described in \\Cref{source-tiers}), recording their ",
        ", ".join([record.replace("(\\Cref", "(see \\Cref") for record in toRecord]),
        f"\\ as applicable."]
    if sec == "Intro":
        methodOverview.append(
            f"We also record any {OTHER_NOTES}, such as {OTHER_NOTES_EXS}.%")

    # Textual methodology overviews
    writeFile(methodOverview, f"methodOverview{sec}", helper=True)
