"""Decide whether a referenced work is a pure mathematical ancestor.

The target quantity is how AI consumes *pure* theoretical mathematics that
was developed independently of AI. Mathematics produced under AI influence
(neural tangent kernels, optimiser convergence bounds, generalisation
theory) is reverse flow and must not count as an ancestor, or the lead-lag
signal is compressed or inverted.

Provenance is judged from two reliable sources rather than from OpenAlex
topic tags, which mislabel pure-math references as CS often enough to be
unusable (a pure optimal-transport paper came out 53% "AI-referenced"
under the tag method, 0% under this one):

  - AI side:   the reference's publication venue is on the AI whitelist.
  - Math side: the reference is indexed in zbMATH, or sits in a math venue.

A work is a pure mathematical ancestor when its own references are
math-dominated and not AI-dominated.
"""
import time
import urllib.parse

AI_VENUE_PATTERNS = [
    "neural information processing", "neurips", "nips",
    "international conference on machine learning", "icml",
    "computer vision and pattern recognition", "cvpr", "iccv", "eccv",
    "international conference on learning representations", "iclr",
    "aaai", "ijcai", "empirical methods in natural language", "emnlp", "acl ",
    "journal of machine learning research", "jmlr", "machine learning",
    "artificial intelligence", "knowledge discovery", "kdd", "siggraph",
    "transactions on pattern analysis", "transactions on neural networks",
    "advances in neural",
]

MATH_VENUE_HINTS = [
    "mathemat", "annals of", "inventiones", "acta ", "journal of functional",
    "communications on pure", "siam journal", "numerische",
    "calculus of variations", "probability", "topology", "geometry", "algebra",
]


def is_ai_venue(venue_name):
    n = (venue_name or "").lower()
    return any(p in n for p in AI_VENUE_PATTERNS)


def is_math_venue(venue_name):
    n = (venue_name or "").lower()
    return any(h in n for h in MATH_VENUE_HINTS)


def in_zbmath(doi, session, cache, pause=0.05):
    """True if the DOI resolves to a zbMATH record (cached, rate-limited)."""
    if not doi:
        return False
    if doi in cache:
        return cache[doi]
    q = urllib.parse.quote("doi:%s" % doi)
    hit = False
    try:
        r = session.get(
            "https://api.zbmath.org/v1/document/_search"
            "?search_string=%s&page=0&results_per_page=1" % q, timeout=20)
        hit = r.status_code == 200 and len(r.json().get("result", [])) > 0
    except Exception:
        hit = False
    cache[doi] = hit
    time.sleep(pause)
    return hit


def classify_reference(ref, session, zb_cache, allow_zbmath=True):
    """Label a single reference as 'ai', 'math', or 'other'."""
    venue = ((ref.get("primary_location") or {}).get("source") or {}).get(
        "display_name", "")
    if is_ai_venue(venue):
        return "ai"
    doi = (ref.get("doi") or "").replace("https://doi.org/", "")
    if is_math_venue(venue):
        return "math"
    if allow_zbmath and in_zbmath(doi, session, zb_cache):
        return "math"
    return "other"


def is_pure_math_ancestor(ref_labels, ai_ceiling=0.15, math_floor=0.40):
    """A work is a pure ancestor when its references are math-dominated and
    not AI-dominated. Thresholds are pilot defaults, tuned against the
    known-case validation set."""
    n = len(ref_labels)
    if n == 0:
        return False
    ai = ref_labels.count("ai") / n
    math = ref_labels.count("math") / n
    return ai <= ai_ceiling and math >= math_floor
