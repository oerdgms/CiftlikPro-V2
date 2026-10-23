"""Shared, read-only partial text matching for list and picker searches."""
import unicodedata


def normalize(value):
    text = unicodedata.normalize('NFKD', str(value or '').casefold().replace('ı', 'i'))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return ' '.join(''.join(ch if ch.isalnum() else ' ' for ch in text).split())


def matches(query, *values):
    words = normalize(query).split()
    haystack = normalize(' '.join(str(value or '') for value in values))
    return all(word in haystack for word in words)
