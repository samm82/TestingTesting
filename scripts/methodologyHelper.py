import re
    
from helpers import capFirst, wrapEnv, writeFile

CAT_FOOTNOTE = "\n\t".join([
    "\\footnote{",
    "There may be more than one category given for a single test approach ",
    "\\ifnotpaper (for example, A/B Testing in \\Cref{tab:approachGlossaryExcerpt}) \\fi ",
    "which is indicative of a flaw (see \\Cref{multiCats}).} \n"])
toRecord: list[str] = [
    "name", f"category{CAT_FOOTNOTE}(\\Cref{{categories-observ}})",
    "definition", "synonyms (\\Cref{syn-rels})",
    "parents (\\Cref{par-chd-rels})",
    "flaws\\phantomsection{}\\label{manual-flaws} (in a separate document)\
    \\latertodo{Define in \\nameref{terminology}; \\thesisissuerefhelper{140}}"]

OTHER_NOTES = "other relevant notes"
OTHER_NOTES_EXS = ", ".join(["prerequisites", "uncertainties",
                             "and other resources"])

methodology_a = """    \\item \\phantomsection{}\\label{identify-sources}
          Identify authoritative sources \\ifnotpaper on software testing \\fi (\\Cref{sources})
    \\item \\phantomsection{}\\label{identify-terms}
          Identify software testing terminology from each source, including
          test approaches and terms that imply them (\\Cref{derived-tests})
    \\item \\phantomsection{}\\label{record-terms}
          For each test approach, record its: (\\Cref{procedure})\n""" + "\n".join([
        f"\t\t  {line}" for line in wrapEnv(
            "enumerate", [f"\t\\item {capFirst(i)}"
                          for i in toRecord + [OTHER_NOTES +
                                               f" (e.g., {OTHER_NOTES_EXS})"]])
        ]) + """\n    \\item Repeat steps~\\ref{identify-sources} to
          \\ref{record-terms} on any subsets of terminology that are missing or
          unclear (\\Cref{undef-terms}) until some stopping criteria
          \\imptodo{Define/add pointer}"""
    
methodology_b = """    \\item Analyze recorded test approach data for additional flaws
          \\begin{enumerate}
              \\item Generate relation graphs (\\Cref{\\ifnotpaper graph-gen\\else tools\\fi})
              \\item Automatically detect certain classes of flaws
                    \\ifnotpaper (\\Cref{auto-flaw-analysis}) \\fi
              \\item Automatically analyze manually recorded flaws from
                    step~\\ref{manual-flaws} \\ifnotpaper (\\Cref{aug-flaw-analysis}) \\fi
          \\end{enumerate}
    \\item Report results of flaw analysis (\\Cref{flaws})
    \\item Provide examples of how to resolve these flaws (\\Cref{recs})"""
    
# Base methodology overview
writeFile(wrapEnv("enumerate", [methodology_a, methodology_b]),
          "methodOverview", helper=True)

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
                  "\\ref{record-terms}.\\ref{manual-flaws}")

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
