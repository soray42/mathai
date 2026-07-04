"""Collect each conference seed's references from Semantic Scholar, storing title +
abstract + fieldsOfStudy + year locally so provenance judging can run later WITHOUT
any live API dependency. Decouples acquisition from judging (user's plan).

Seeds come from dblp conference tocs (build via nightly_pipeline stage 1, or here we
locate each seed on S2 by title search). S2 gives references (with cited-paper
abstracts) in one call. Strict serial requests + backoff (key ~1 req/s cumulative).

Output JSONL rows (one per seed):
  {venue, layer, seed_year, title, s2_id, refs:[{title,year,abstract,fos,extIds}]}
Resumable: skips seeds whose title already appears in the output.
"""
import os, sys, json, time, re, requests
import urllib.request, urllib.parse
import pypdfium2 as pdfium

KEY = os.environ["S2_API_KEY"]     # never hardcode; set via .env (gitignored)
H = {"x-api-key": KEY}
BASE = "https://api.semanticscholar.org/graph/v1"
GAP = 1.3          # base spacing (below 1/s nominal after backoff)
OUT = "data/interim/seeds_refs_s2.jsonl"


def s2get(path, params, maxtry=7):
    for a in range(maxtry):
        try:
            r = requests.get(BASE + path, params=params, headers=H, timeout=40)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:
                return None
        except Exception:
            pass
        time.sleep(GAP + 2.2 * a)     # escalating backoff on 429/error
    return "FAIL"


def find_seed_id(title):
    j = s2get("/paper/search", {"query": title, "fields": "title,externalIds", "limit": 1})
    if j in (None, "FAIL") or not j.get("data"):
        return None
    return j["data"][0].get("paperId")


def get_refs(sid):
    j = s2get(f"/paper/{sid}/references",
              {"fields": "title,year,abstract,externalIds,fieldsOfStudy", "limit": 200})
    if j in (None, "FAIL"):
        return j                       # transient — retry next run
    data = j.get("data") or []          # S2 returns data:null for papers it can't resolve
    out = []
    for e in data:
        c = (e.get("citedPaper") or {})
        out.append({"title": c.get("title"), "year": c.get("year"),
                    "abstract": c.get("abstract"), "fos": c.get("fieldsOfStudy"),
                    "s2_id": c.get("paperId"), "extIds": c.get("externalIds")})
    return out                          # [] means S2 genuinely has no structured refs


def arxiv_find_id(title):
    """Locate a paper on arXiv by exact-ish title; return arXiv id or None."""
    q = urllib.parse.quote(f'ti:"{title}"')
    url = f"http://export.arxiv.org/api/query?search_query={q}&max_results=1"
    try:
        x = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mathai-research/1.0"}),
                                   timeout=30).read().decode()
        m = re.search(r"arxiv\.org/abs/([\w.]+)", x)
        return m.group(1) if m else None
    except Exception:
        return None


def arxiv_bib_titles(aid):
    """Download arXiv PDF, parse bibliography into raw reference strings.
    Returns list of {raw, arxiv_id} — coarse but budget-free fallback."""
    try:
        data = urllib.request.urlopen(
            urllib.request.Request(f"https://arxiv.org/pdf/{aid}", headers={"User-Agent": "mathai-research/1.0"}),
            timeout=45).read()
        open("/tmp/seedpdf.pdf", "wb").write(data)
        pdf = pdfium.PdfDocument("/tmp/seedpdf.pdf")
        text = "".join(pdf[i].get_textpage().get_text_range() for i in range(len(pdf)))
    except Exception:
        return []
    i = text.lower().rfind("references")
    if i < 0:
        return []
    bib = text[i + len("references"):]
    # split on [n] markers; keep each entry's raw text + any arXiv id inside
    parts = re.split(r"\[\d+\]", bib)
    out = []
    for p in parts:
        p = re.sub(r"\s+", " ", p).strip()
        if len(p) < 20:
            continue
        m = re.search(r"(\d{4}\.\d{4,5})", p)
        out.append({"raw": p[:300], "arxiv_id": m.group(1) if m else None})
    return out


def done_titles():
    seen = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                seen.add(json.loads(line)["title"])
            except Exception:
                pass
    return seen


def load_seeds(shard_files):
    seeds = []
    for f in shard_files:
        if not os.path.exists(f):
            continue
        for line in open(f):
            r = json.loads(line)
            if r.get("empty"):
                continue
            seeds.append((r["venue"], r.get("layer", "?"), r["seed_year"], r["title"]))
    return seeds


def main():
    # seed source = pure-dblp seed files; shardable by suffix list in argv[1]
    src_suffixes = sys.argv[1].split(",") if (len(sys.argv) > 1 and sys.argv[1]) else \
        ["theory", "method", "dmnlp"]
    out_suffix = sys.argv[2] if len(sys.argv) > 2 else "all"
    global OUT
    OUT = f"data/interim/seeds_refs_{out_suffix}.jsonl"
    shard_files = [f"data/interim/seeds_dblp_{s}.jsonl" for s in src_suffixes]
    seeds = load_seeds(shard_files)
    seen = done_titles()
    fout = open(OUT, "a")
    n_done = n_fail = n_arxiv = 0
    for i, (venue, layer, sy, title) in enumerate(seeds):
        if title in seen:
            continue
        sid = find_seed_id(title)
        time.sleep(GAP)
        if not sid:
            fout.write(json.dumps({"venue": venue, "layer": layer, "seed_year": sy,
                                   "title": title, "s2_id": None, "refs": [],
                                   "ref_source": "none", "note": "seed_not_found"},
                                  ensure_ascii=False) + "\n")
            fout.flush(); n_fail += 1; continue
        refs = get_refs(sid)
        time.sleep(GAP)
        if refs in (None, "FAIL"):
            n_fail += 1                 # transient rate error — retry next run
            continue
        ref_source = "s2"
        if not refs:
            # S2 genuinely has no structured refs -> arXiv bib fallback
            aid = arxiv_find_id(title)
            time.sleep(3.2)             # arXiv politeness
            if aid:
                bib = arxiv_bib_titles(aid)
                if bib:
                    refs = [{"title": None, "year": None, "abstract": None, "fos": None,
                             "s2_id": None, "extIds": {"ArXiv": b["arxiv_id"]},
                             "raw_bib": b["raw"]} for b in bib]
                    ref_source = f"arxiv:{aid}"
                    n_arxiv += 1
                time.sleep(2)
        fout.write(json.dumps({"venue": venue, "layer": layer, "seed_year": sy,
                               "title": title, "s2_id": sid, "refs": refs,
                               "ref_source": ref_source}, ensure_ascii=False) + "\n")
        fout.flush(); n_done += 1
        if n_done % 25 == 0:
            print(f"[{i}/{len(seeds)}] done={n_done} arxiv_fb={n_arxiv} "
                  f"fail={n_fail} last={venue}{sy}", flush=True)
    fout.close()
    print(f"DONE collected={n_done} arxiv_fallback={n_arxiv} failed={n_fail}", flush=True)


if __name__ == "__main__":
    main()
