"""Layer assignment for CORE AI(4602)+ML(4611) A*/A/B venues.

Three layers by the KIND of math consumption we expect:
  theory  : learning theory / optimization / automated reasoning / logic —
            consumes and produces frontier + AI-induced mathematics.
  method  : core ML/AI methods venues — consume math (mostly established),
            produce empirical methods; shallow-but-real math consumption.
  applied : application/engineering venues (robotics, speech, web, NLP-applied,
            evolutionary/fuzzy, agents, software) — low direct math consumption.

dblp stream keys map acronym -> conf/<stream>/<stream><year>. A venue enters the
seed set only for years it was A*/A/B in THAT year's CORE edition (handled at pull
time); this file is the static layer map. Acronyms not resolvable in dblp for a
given year are simply skipped.
"""

LAYER = {
    # --- theory layer ---
    "COLT": "theory", "ALT": "theory", "UAI": "theory", "AISTATS": "theory",
    "CADE": "theory", "IJCAR": "theory", "SAT": "theory", "KR": "theory",
    "LPAR": "theory", "LPNMR": "theory", "JELIA": "theory", "CP": "theory",
    "ICAPS": "theory", "SoCS": "theory", "FOGA": "theory", "EC": "theory",

    # --- method layer (core ML/AI) ---
    "NeurIPS": "method", "ICML": "method", "ICLR": "method", "AAAI": "method",
    "IJCAI": "method", "ECML PKDD": "method", "KDD": "method", "ICDM": "method",
    "ECAI": "method", "ACL": "method", "EMNLP": "method", "NAACL": "method",
    "AAMAS": "method", "CIKM": "method", "WSDM": "method", "ICONIP": "method",
    "ESANN": "method", "IJCNN": "method",

    # --- applied / engineering layer ---
    "ICRA": "applied", "IROS": "applied", "HRI": "applied", "Interspeech": "applied",
    "SIGSPATIAL": "applied", "GECCO": "applied", "PPSN": "applied", "CEC": "applied",
    "IEEE-IV": "applied", "BigData": "applied", "COLING": "applied", "EACL": "applied",
    "IJCNLP": "applied", "CoNLL": "applied", "INLG": "applied", "SIGdial": "applied",
    "LREC": "applied", "FUZZ-IEEE": "applied", "CogSci": "applied",
}

# dblp stream key overrides where acronym != stream name
DBLP_STREAM = {
    "NeurIPS": "nips", "ECML PKDD": "pkdd", "ICLR": "iclr", "Interspeech": "interspeech",
    "AISTATS": "aistats", "EMNLP": "emnlp", "NAACL": "naacl", "AAMAS": "atal",
}

PRIORITY = ["theory", "method", "applied"]
