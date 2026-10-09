"""
Knuth-Morris-Pratt (KMP) Pattern Matching Algorithm.
Time Complexity: O(N + M) where N = len(text), M = len(pattern).
Space Complexity: O(M) for LPS array.
Used for exact searching of patient names, medical IDs, doctor specialties, and ward names.
"""

from typing import List

def compute_lps(pattern: str) -> List[int]:
    """
    Computes the Longest Prefix Suffix (LPS) array for KMP algorithm.
    lps[i] stores the length of the longest proper prefix of pattern[0..i]
    that is also a suffix of pattern[0..i].
    """
    m = len(pattern)
    lps = [0] * m
    length = 0  # length of previous longest prefix suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str, case_sensitive: bool = False) -> List[int]:
    """
    Performs KMP exact string matching to find all occurrences of pattern in text.
    Returns a list of starting 0-indexed positions in text.
    """
    if not pattern or not text:
        return []
    
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()

    n = len(text)
    m = len(pattern)
    if m > n:
        return []

    lps = compute_lps(pattern)
    matches = []

    i = 0  # index for text
    j = 0  # index for pattern

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            matches.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return matches
