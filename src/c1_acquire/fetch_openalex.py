"""Fetch the math->AI citation subgraph from OpenAlex.

Draws a reproducible AI/CS seed set (fetch_seed_set), walks their
referenced_works one hop to pull in the mathematical ancestry
(expand_references), and builds the directed citing->cited edge list
(edge_list). These functions return in-memory records; persistence and the
data-version stamp are the caller's job (see c1_acquire.build_seed_set, which
writes the pinned tables under data/interim).

The reference walk fetches works in batches through the openalex_id filter
(up to 100 ids per request) rather than one work at a time, and every
request goes through _get_json, which retries with backoff and raises on
persistent failure. An earlier version dropped the per-request pause and
swallowed exceptions, so rate-limit responses were silently discarded and a
large batch came back empty; both of those are fixed here.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

WORKS = "https://api.openalex.org/works"
UA = "mathai-research"
BATCH = 100          # openalex_id filter accepts up to 100 ids per request
PAUSE = 0.2          # polite gap between requests, always kept
MAX_RETRY = 5
SELECT = "id,doi,title,publication_year,referenced_works,referenced_works_count,primary_topic,concepts"


def _get_json(params, max_retry=MAX_RETRY):
    """GET the works endpoint with retry + backoff. Raises on give-up.

    Retries on rate-limit (429) and transient 5xx / URL errors with an
    exponential backoff. Never returns a partial or empty payload silently:
    if every attempt fails the exception propagates so the caller stops.
    """
    params = dict(params)
    params.setdefault("api_key", os.environ["OPENALEX_API_KEY"])
    url = WORKS + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(max_retry):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503):
                time.sleep(2 ** attempt)
                continue
            raise
        except urllib.error.URLError as e:
            last = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"OpenAlex request failed after {max_retry} tries: {last}")


def fetch_seed_set(year_range, per_year, seed, subfield="1702"):
    """Reproducibly sample the AI/CS seed papers to start the walk from.

    For each year in year_range (inclusive) draw `per_year` works from the
    given OpenAlex subfield that have references, using OpenAlex deterministic
    sampling (sample + seed) so the seed set rebuilds exactly. Returns a list
    of full work records.
    """
    y0, y1 = year_range
    seeds = []
    for year in range(y0, y1 + 1):
        data = _get_json({
            "filter": (f"primary_topic.subfield.id:subfields/{subfield},"
                       f"has_references:true,publication_year:{year}"),
            "sample": per_year, "seed": seed, "per-page": per_year,
            "select": SELECT,
        })
        got = data.get("results", [])
        if len(got) < per_year:
            print(f"  warn: {year} returned {len(got)}/{per_year}")
        seeds.extend(got)
        print(f"  {year}: {len(got)} seeds")
        time.sleep(PAUSE)
    return seeds


def expand_references(ref_ids):
    """Fetch the reference works (1-hop ancestors) in batches.

    ref_ids: iterable of OpenAlex work ids. Returns a dict id -> work record
    (year, referenced_works, etc.), which is what the age model and the
    provenance filter both consume. De-duplicates before fetching.
    """
    uniq = list(dict.fromkeys(ref_ids))
    short = [i.rsplit("/", 1)[-1] for i in uniq]
    out = {}
    for k in range(0, len(short), BATCH):
        chunk = short[k:k + BATCH]
        data = _get_json({
            "filter": "openalex_id:" + "|".join(chunk),
            "per-page": BATCH, "select": SELECT,
        })
        for w in data.get("results", []):
            out[w["id"]] = w
        if (k // BATCH) % 20 == 0:
            print(f"  refs {k + len(chunk)}/{len(short)} fetched")
        time.sleep(PAUSE)
    return out


def edge_list(seeds, ref_ids_kept):
    """Directed citing->cited edges, keeping only edges into ref_ids_kept.

    ref_ids_kept is the set of reference ids that survived the provenance /
    math filter; edges to anything else are dropped.
    """
    keep = set(ref_ids_kept)
    edges = []
    for w in seeds:
        src = w["id"]
        for dst in (w.get("referenced_works") or []):
            if dst in keep:
                edges.append((src, dst))
    return edges


if __name__ == "__main__":
    pass
