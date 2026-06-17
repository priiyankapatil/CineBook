"""
Sentiment Analysis for user reviews.

Uses TextBlob (which uses NLTK's VADER lexicon under the hood).
No training needed — it's a pre-trained rule-based model.

Returns a float between -1.0 (very negative) and +1.0 (very positive).
Handles read-only filesystems (e.g. Vercel serverless) gracefully.
"""

import os
import nltk
from textblob import TextBlob

def _ensure_nltk_resource(resource_id, download_name=None):
    if download_name is None:
        download_name = resource_id
    try:
        nltk.data.find(resource_id)
        return
    except LookupError:
        pass
    try:
        nltk.download(download_name, quiet=True)
        return
    except OSError:
        pass
    alt_path = os.path.join('/tmp', 'nltk_data')
    nltk.data.path.insert(0, alt_path)
    try:
        nltk.data.find(resource_id)
        return
    except LookupError:
        pass
    try:
        nltk.download(download_name, download_dir=alt_path, quiet=True)
    except OSError:
        pass

_ensure_nltk_resource('tokenizers/punkt', 'punkt')
_ensure_nltk_resource('corpora/wordnet', 'wordnet')


def analyze_sentiment(text):
    """
    Analyze the sentiment of a review text.

    Parameters
    ----------
    text : str
        The review text to analyze.

    Returns
    -------
    float
        Polarity score from -1.0 (negative) to +1.0 (positive).
        0.0 is neutral. Returns None if text is empty.
    """
    if not text or not text.strip():
        return None

    blob = TextBlob(text.strip())
    return round(blob.sentiment.polarity, 3)
