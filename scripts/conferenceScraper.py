import requests, re
from bs4 import BeautifulSoup

from datetime import datetime


ignore = {"NYC-2024-SE 2024", "SOFT 2024", "C3S2E 2024", "APCS 2024", "IEEE ICICT 2024", "SEKE 2024", "CSTY 2024",
          "DMSE  2024", "SEA 2024", "SOENG  2024", "AIFU 2024", "CETA 2024", "ICSCT 2024", "ICSTE 2024"}
# To distinguish conferences I was unsure about excluding from those I was certain about excluding
maybeIrrelevant = {"ICCS 2024", "ACM ICBDT 2024", "ICCDA 2024", "ICCSN 2024", "ACM CCIOT 2024", "ACM ICAIP 2024",
                   "ACM ICCPR 2024", "IEEE CECCC 2024", "ICVIP--EI 2024", "IOTSMS 2024", "IEEE ICCC 2024",
                   "ISCMI 2024", "ADIP 2024", "ACM AICCC 2024", "AIAT 2024", "ICGIP--EI 2024", "ICNCC 2024",
                   "ACM VRIP 2024", "ACM BDCI 2024", "ACM DMIP 2024", "ACM MLMI 2024", "BMSD 2024", "IPAI 2024",
                   "IEEE ICRCV 2024", "BIOTC 2024", "IEEE WSAI 2024", "QSE-NE 2024", "ACM ICDLT 2024",
                   "SPIE ICDIP 2024", "IWIP 2024", "IEEE SSE 2024", "MODELS 2024", "ISSM 2024",
                   "ICCMS 2024", "ICMIS--ESCI 2024"}

# categories on WikiCFP (http://www.wikicfp.com/cfp/allcat)
categories = {"software testing", "software engineering"}
# key"word"s that exclude a conference if they are present in its title
# e.g., note the spaces in " ai " to specifcally filter out artificial intelligence
ignoredTopics = {"image", "deep", "robot", "machine", "intelli", "data", "vision", "high performance", "cloud",
                 "communi", "blockchain", "parallel", "distributed", "signal", " ai ", "crypto"}

# For setting a target deadline for when you think you'll be ready by
DEADLINE_YEAR = 2024
DEADLINE_MONTH = "May"

HEADER_PREFIX = "## "
INFO_PREFIX = "- "

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

TODAY = int(datetime.now().strftime("%d"))
THIS_MONTH = datetime.now().strftime('%h')

for cat in categories:
    print(cat.upper(), "\n")
    cat = cat.replace(" ", "%20")
    page = 1
    keepLooking = True
    while keepLooking:
        URL = f"http://www.wikicfp.com/cfp/call?conference={cat}&page={page}"
        try:
            webpage = requests.get(URL)
        except:
            keepLooking = False
            break

        soup = BeautifulSoup(webpage.content, "html.parser")
        results = soup.find("div", class_="contsec")
        # Filter to Canada or the US
        # possible = results.find_all("td", string=lambda t: t and any(x in t.lower() for x in ("canada", "states", "usa")))
        possible = results.find_all("td", string=re.compile("^[a-zA-Z ]*,[a-zA-Z ]*$"))
        possible = [p for p in possible if not p.get("colspan")]
        for p in possible:
            submission = p.find_next_sibling("td").text
            year = int(submission.strip(")").split()[-1])
            try:
                if year < DEADLINE_YEAR:
                    keepLooking = False
                    break
                if year == DEADLINE_YEAR and any(m in submission for m in MONTHS[:MONTHS.index(DEADLINE_MONTH)]):
                    continue
                if THIS_MONTH == DEADLINE_MONTH and DEADLINE_MONTH in submission and \
                    int(submission.split()[-2].strip(",")) < TODAY:
                    continue
            except:
                print(submission)
                exit()
            conf = p.find_previous_sibling("td").parent.find_previous_sibling("tr").find_all("td")
            if conf[0].text not in ignore and conf[0].text not in maybeIrrelevant:
                if not any(t in conf[1].text.lower() for t in ignoredTopics):
                    print(f"{HEADER_PREFIX}{conf[0].text}: {conf[1].text}")
                    print(f"{INFO_PREFIX}{p.find_previous_sibling("td").text} in {p.text} | Submission Date: {submission}\n")
        
        page += 1
