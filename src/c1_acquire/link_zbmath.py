"""Attach MSC subject classes to the math side of the graph via zbMATH.

OpenAlex native topics are too coarse and mis-disambiguated to use as a
subject label, so we match papers to zbMATH and take its MSC codes. The
match-rate curve this produces is a go/no-go gate: below the threshold we
fall back to the trained classifier in train_msc_classifier.py.
"""
from pathlib import Path


def match_openalex_to_zbmath(papers):
    """Match on DOI first, then title+year fuzzy match. Return match table."""
    # TODO: query the zbMATH structured search endpoint, record hit/miss
    raise NotImplementedError


def match_rate_by_year(match_table):
    """Coverage curve used for the C1 go/no-go decision."""
    # TODO: group by publication year, report matched fraction
    raise NotImplementedError


if __name__ == "__main__":
    pass
