"""Extrapolate MSC labels when zbMATH coverage is too thin.

Uses the zbMATH-matched papers as training data and predicts MSC classes
for the unmatched remainder from title/abstract features. Only invoked
when link_zbmath.py reports coverage below the configured floor.
"""


def build_training_set(match_table):
    """Positive examples = papers with a confirmed zbMATH MSC label."""
    raise NotImplementedError


def train(features, labels):
    """Fit the subject classifier. Report held-out F1 before extrapolating."""
    raise NotImplementedError


def predict_unmatched(model, unmatched):
    raise NotImplementedError


if __name__ == "__main__":
    pass
