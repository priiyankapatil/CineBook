"""
Sentiment Analysis for user reviews.

Uses TextBlob (which uses NLTK's VADER lexicon under the hood).
No training needed — it's a pre-trained rule-based model.

Returns a float between -1.0 (very negative) and +1.0 (very positive).
"""

from textblob import TextBlob
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)


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
