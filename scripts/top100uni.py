unis = """Massachusetts Institute of Technology
MIT
University of Cambridge
University of Oxford
Harvard University
Stanford University
Imperial College London
ETH Zurich
Swiss Federal Institute of Technology
National University of Singapore
NUS
UCL
University College London
University of California, Berkeley
University of California Berkeley
University of California
University of Berkeley
UCB
University of Chicago
University of Pennsylvania
Cornell University
University of Melbourne
California Institute of Technology
Caltech
Yale University
Peking University
Princeton University
University of New South Wales
UNSW Sydney
University of Sydney
University of Toronto
University of Edinburgh
Columbia University
Universite PSL
PSL
Tsinghua University
Nanyang Technological University, Singapore
Nanyang Technological University Singapore
Nanyang Technological University
NTU
NTUS
University of Hong Kong
UKU
Johns Hopkins University
John Hopkins University
Johns Hopkin's University
John's Hopkins University
John's Hopkin's University
University of Tokyo
University of California, Los Angeles
University of California Los Angeles
University of Los Angeles
University of LA
UCLA
McGill University
McGill
University of Manchester
University of Michigan-Ann Arbor
University of Michigan, Ann Arbor
University of Michigan Ann Arbor
University of Michigan
Australian National University
University of British Columbia
Ecole Polytechnique Fédérale de Lausanne
Ecole Polytechnique Federale de Lausanne
EPFL
Technical University of Munich
Institut Polytechnique de Paris
New York University
NYU
King's College London
Kings College London
Seoul National University
Monash University
University of Queensland
Zhejiang University
London School of Economics and Political Science
LSE
Kyoto University
Delft University of Technology
Northwestern University
Chinese University of Hong Kong
CUHK
Fudan University
Shanghai Jiao Tong University
Carnegie Mellon University
University of Amsterdam
Ludwig-Maximilians-Universität München
Ludwig Maximilians Universität München
Ludwig-Maximilians-Universitat Munchen
Ludwig Maximilians Universitat Munchen
University of Bristol
KAIST - Korea Advanced Institute of Science & Technology
KAIST
Korea Advanced Institute of Science & Technology
Korea Advanced Institute of Science and Technology
Duke University
University of Texas at Austin
Sorbonne University
Hong Kong University of Science and Technology
HKUST
KU Leuven
University of California, San Diego
University of California San Diego
University of San Diego
UCSD
University of Washington
University of Illinois at Urbana-Champaign
University of Illinois at Urbana Champaign
University of Urbana-Champaign
University of Urbana Champaign
University of Illinois
Hong Kong Polytechnic University
Universiti Malaya
UM
University of Warwick
University of Auckland
National Taiwan University
NTU
City University of Hong Kong
Universite Paris-Saclay
Universite Paris Saclay
University of Western Australia
Brown University
KTH Royal Institute of Technology
KTH
Royal Institute of Technology
University of Leeds
University of Glasgow
Yonsei University
Durham University
Korea University
Osaka University
Trinity College Dublin, The University of Dublin
Trinity College Dublin
The University of Dublin
University of Dublin
University of Southampton
Pennsylvania State University
University of Birmingham
Lund University
Universidade de São Paulo
Universidade de Sao Paulo
University of São Paulo
University of Sao Paulo
Lomonosov Moscow State University
Universität Heidelberg
Universitat Heidelberg
The University of Adelaide
University of Technology Sydney
Tokyo Institute of Technology
University of Zurich
Boston University
Universidad Nacional Autónoma de México
Universidad Nacional Autonoma de Mexico
UNAM
Universidad de Buenos Aires
UBA
University of St Andrews
University of St. Andrews
University of St. Andrew's
University of St Andrew's
University of Saint Andrew's
University of Saint Andrews
Georgia Institute of Technology
Freie Universitaet Berlin
Purdue University
Pohang University of Science and Technology
POSTECH
University of Nottingham
McMaster
McMaster University""".split("\n")
# This list is based on https://www.topuniversities.com/student-info/choosing-university/worlds-top-100-universities
# I added McMaster; feel free to remove

conf = """ADD COMMITTEE LIST HERE
""".replace("’", "'").replace("‘", "'").replace(" - ", ", ").split("\n")

# for if universities are the second element in a comma-separated list
# conf = [", ".join(c.strip().split(", ")[1:]) for c in conf]

# for if universities are the second-LAST element in a comma-separated list
# conf = [", ".join(c.strip().split(", ")[-2:-1]) for c in conf]

# for if universities are the center element in a three element, comma-separated list
# conf = [", ".join(c.strip().split(", ")[1:-1]) for c in conf]

for x in conf:
    # Other exceptions may be desirable to add, such as certain companies
    if x in unis or "IEEE" in x:
        print(x)

print(len([x for x in conf if x in unis or "IEEE" in x]), len(conf))
