"""Parse the full dblp dump (data/raw/dblp.xml.gz) and extract EVERY paper from the
41 target venues in VENUES (CORE A*/A/B, fields AI 4602 + ML 4611) for 2013-2025 — no
per-venue-year quota. Each stream prefix below was verified present in the dump by
direct count (e.g. nips 16k, aaai 31k, colt 2.5k inproceedings). Streams the 1GB gz
(never fully in memory), keying on conf/<stream>/ prefixes. Handles split-volume
proceedings automatically (all volumes share the conf/<stream>/ key prefix) and merges
alias streams (ICAPS=aips+icaps, AAMAS=atal+aamas).

Output: data/interim/seeds_dblp_full.jsonl  {venue, layer, stream, seed_year, title, dblp_key}
"""
import gzip, re, json, html

# acronym -> (list of dblp stream prefixes, layer). Verified against dump stream counts.
VENUES = {
    # theory
    "COLT": (["colt"], "theory"), "ALT": (["alt"], "theory"),
    "UAI": (["uai"], "theory"), "AISTATS": (["aistats"], "theory"),
    "CADE": (["cade"], "theory"), "IJCAR": (["ijcar"], "theory"),
    "SAT": (["sat"], "theory"), "KR": (["kr"], "theory"),
    "LPAR": (["lpar"], "theory"), "LPNMR": (["lpnmr"], "theory"),
    "JELIA": (["jelia"], "theory"), "CP": (["cp"], "theory"),
    "ICAPS": (["icaps", "aips"], "theory"), "FOGA": (["foga"], "theory"),
    "EC": (["sigecom"], "theory"),
    # method
    "NeurIPS": (["nips"], "method"), "ICML": (["icml"], "method"),
    "ICLR": (["iclr"], "method"), "AAAI": (["aaai"], "method"),
    "IJCAI": (["ijcai"], "method"), "KDD": (["kdd"], "method"),
    "ICDM": (["icdm"], "method"), "ECAI": (["ecai"], "method"),
    "ACL": (["acl"], "method"), "EMNLP": (["emnlp"], "method"),
    "NAACL": (["naacl"], "method"), "AAMAS": (["atal", "aamas"], "method"),
    "CIKM": (["cikm"], "method"), "WSDM": (["wsdm"], "method"),
    # applied
    "ICRA": (["icra"], "applied"), "IROS": (["iros"], "applied"),
    "HRI": (["hri"], "applied"), "Interspeech": (["interspeech"], "applied"),
    "GECCO": (["gecco"], "applied"), "CEC": (["cec"], "applied"),
    "COLING": (["coling"], "applied"), "EACL": (["eacl"], "applied"),
    "IJCNLP": (["ijcnlp"], "applied"), "CoNLL": (["conll"], "applied"),
    "LREC": (["lrec"], "applied"), "BigData": (["bigdataconf"], "applied"),
}

# stream prefix -> (venue, layer)
STREAM2VENUE = {}
for ven, (streams, layer) in VENUES.items():
    for s in streams:
        STREAM2VENUE[s] = (ven, layer)

DUMP = "data/raw/dblp.xml.gz"
OUT = "data/interim/seeds_dblp_full.jsonl"
Y0, Y1 = 2013, 2025


def main():
    key_re = re.compile(r'<inproceedings[^>]*key="conf/([^/]+)/[^"]*"')
    title_re = re.compile(r"<title>(.*?)</title>", re.S)
    year_re = re.compile(r"<year>(\d{4})</year>")
    fout = open(OUT, "w")
    buf = []
    inrec = False
    n_written = 0
    counts = {}
    with gzip.open(DUMP, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not inrec and "<inproceedings" in line:
                inrec = True
                buf = [line]
                continue
            if inrec:
                buf.append(line)
                if "</inproceedings>" in line:
                    inrec = False
                    rec = "".join(buf)
                    km = key_re.search(rec)
                    if not km:
                        continue
                    stream = km.group(1)
                    if stream not in STREAM2VENUE:
                        continue
                    ym = year_re.search(rec)
                    if not ym:
                        continue
                    year = int(ym.group(1))
                    if not (Y0 <= year <= Y1):
                        continue
                    tm = title_re.search(rec)
                    if not tm:
                        continue
                    title = re.sub(r"<.*?>", "", tm.group(1))
                    title = html.unescape(re.sub(r"\s+", " ", title)).strip().rstrip(".")
                    if len(title) < 10 or "proceedings" in title.lower():
                        continue
                    keym = re.search(r'key="(conf/[^"]+)"', rec)
                    ven, layer = STREAM2VENUE[stream]
                    fout.write(json.dumps({"venue": ven, "layer": layer, "stream": stream,
                                           "seed_year": year, "title": title,
                                           "dblp_key": keym.group(1) if keym else None},
                                          ensure_ascii=False) + "\n")
                    n_written += 1
                    counts[ven] = counts.get(ven, 0) + 1
    fout.close()
    print("TOTAL written:", n_written)
    for v in sorted(counts, key=lambda k: -counts[k]):
        print(f"  {v}: {counts[v]}")


if __name__ == "__main__":
    main()
