"""Date the first real appearance of each concept from full text.

Second instrument alongside the citation-based A(p). Consumes the
concept-by-year frequency index from stream_pes2o (it does not re-scan
the corpus), applies a cumulative-frequency threshold, and requires the
concept to show up in at least N papers from independent authors before
accepting a first-use year, so a single self-citing paper cannot forge
an early date.
"""


def cumulative_threshold(freq_series, frac):
    """First year at which cumulative mentions cross the threshold."""
    raise NotImplementedError


def require_independent_support(candidate_year, papers, min_papers):
    """Reject a first-use year backed by too few independent authors."""
    raise NotImplementedError


if __name__ == "__main__":
    pass
