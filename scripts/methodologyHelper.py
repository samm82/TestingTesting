import re
    
from helpers import capFirst, wrapEnv, writeFile

CAT_FOOTNOTE = "\n\t".join([
    "\\footnote{"
    "A single test approach with more than one category ",
    "\\ifnotpaper (for example, A/B Testing in \\Cref{tab:approachGlossaryExcerpt}) \\fi ",
    "indicates an underlying flaw; see \\Cref{multiCats}.} \n"])
toRecord: list[str] = [
    "names", f"categories{CAT_FOOTNOTE}(\\Cref{{categories-observ}})",
    "definitions", "synonyms (\\Cref{syn-rels})",
    "parents (\\Cref{par-chd-rels})",
    "flaws\\phantomsection{}\\label{manual-flaws} (\\Cref{flaw-def}) (in a separate document)"]
relatedTerms: list[str] = [
    "imply related test approaches (\\Cref{derived-tests})",
    "are used repeatedly",
    "have complex definitions"
]

OTHER_NOTES = "other relevant notes"
OTHER_NOTES_EXS = ", ".join(["prerequisites", "uncertainties",
                             "and other resources"])

methodology_a = """
    \\item \\phantomsection{}\\label{identify-sources}
          Identifying authoritative sources \\ifnotpaper on software testing
          \\fi (\\Cref{sources})
    \\item \\phantomsection{}\\label{record-apps}
          Identifying all test approaches from each source and recording their:
          (\\Cref{procedure})\n""" + "\n".join([
        f"\t\t  {line}" for line in wrapEnv(
            "enumerate", [f"\t\\item {capFirst(i)}"
                          for i in toRecord + [OTHER_NOTES +
                                               f" (e.g., {OTHER_NOTES_EXS})"]])
        ]) + """
    \\item \\phantomsection{}\\label{record-terms}
          Alongside step~\\ref{record-apps}, identifying and recording related
          testing terms that:\n""" + "\n".join([
        f"\t\t  {line}" for line in wrapEnv(
            "enumerate", [f"\t\\item {capFirst(i)}" for i in relatedTerms])
          ]) + """
    \\item Repeating steps~\\ref{identify-sources} to
          \\ref{record-terms} for any missing or unclear terms
          (\\Cref{undef-terms}) until some stopping criteria
          \\imptodo{Define/add pointer}"""
    
methodology_b = """    \\item Analyzing recorded test approach data for additional flaws
          \\begin{enumerate}
              \\item Generating relation graphs (\\Cref{\\ifnotpaper graph-gen\\else tools\\fi})
              \\item Automatically detecting certain classes of flaws
                    \\ifnotpaper (\\Cref{auto-flaw-analysis}) \\fi
              \\item Automatically analyzing manually recorded flaws from
                    step~\\ref{manual-flaws} \\ifnotpaper (\\Cref{aug-flaw-analysis}) \\fi
          \\end{enumerate}
    \\item Reporting results of flaw analysis (\\Cref{flaws})
    \\item Providing examples of how to resolve these flaws (\\Cref{recs})"""
    
# Base methodology overview
writeFile(wrapEnv("enumerate", [methodology_a]), "methodOverview", helper=True)

methodOverviewSem = []
m: str
for i, m in enumerate([methodology_a, methodology_b]):
    old_m = ""
    while old_m != m:
        old_m = m
        # From https://stackoverflow.com/a/640016/10002168
        m = re.sub(r"\s+\([^)]*\)", "", m)

    # Hack because enumitem conflicts with beamer :(
    m = m.replace("\\ref{manual-flaws}",
                  "\\ref{record-apps}.\\ref{manual-flaws}")

    if not i:
        PHANTOM_SEC = "phantomsection"
        NEG_SPACE = "\\vspace*{-0.4cm}"
        m = m.split(PHANTOM_SEC)
        # TODO: this is VERY hardcoded
        m[2] = m[2].replace("\\begin{enumerate}",
                            NEG_SPACE + "\\begin{multicols}{3}\\begin{enumerate}")
        m[3] = m[3].replace("\\item Other relevant notes\n", "")
        m[3] = m[3].replace("\\end{enumerate}",
                            # With help from https://tex.stackexchange.com/a/514630/192195
                            # "\\item[\\vspace{\\fill}]"
                            "\\end{enumerate}\\end{multicols}" + NEG_SPACE)
        m = PHANTOM_SEC.join(m)

    mList = m.split("\n")
    # From https://tex.stackexchange.com/a/1702/192195!
    if not i:
        mList.append("\\setcounter{methodCounter}{\\value{enumi}}")
    else:
        mList = (["\\setcounter{enumi}{\\value{methodCounter}}"] + mList[:-1] +
                 ["    \\vspace{0.43cm}", "    \\rqc{}", mList[-1]])

    mList = (["\\framesubtitle{Overview}",
              f"\\rq{"b" if i else "a"}{{}}"] +
             wrapEnv("enumerate", mList))
    methodOverviewSem.append(wrapEnv("frame", "\n\t".join(mList),
                                     param="Methodology"))

# Seminar methodology overview
writeFile(["\n\n".join(methodOverviewSem)], "methodOverviewSem", helper=True)

toRecord[-1] = "and " + toRecord[-1]
methodOverviewIntro = [
    "We start by documenting the \\approachCount{} test approaches mentioned ",
    "by \\srcCount{} sources (described in \\Cref{sources}), recording their ",
    ", ".join([record.replace("(\\Cref", "(see \\Cref") for record in toRecord]),
    f"as applicable. We also record any {OTHER_NOTES}, such as {OTHER_NOTES_EXS}.%"]

# Intro methodology overview
writeFile(methodOverviewIntro, "methodOverviewIntro", helper=True)
