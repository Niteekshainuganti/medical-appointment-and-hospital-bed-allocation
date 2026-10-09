"""
Z-Function String Search Algorithm.
Time Complexity: O(N + M) linear-time exact pattern matching.
Space Complexity: O(N + M) for Z-array.
Used as an alternative exact text-search module for patient/doctor records.
"""

from typing import List

def compute_z_array(s: str) -> List[int]:
    """
    Computes the Z-array for string s.
    Z[i] is the length of the longest common prefix between s and s[i..end].
    """
    n = len(s)
    z = [0] * n
    z[0] = n
    l, r = 0, 0

    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l = i
            r = i + z[i] - 1

    return z


def z_search(text: str, pattern: str, case_sensitive: bool = False) -> List[int]:
    """
    Finds all occurrences of pattern in text using the Z-algorithm.
    Concatenates string concat_s = pattern + '$' + text and computes Z-array.
    Returns 0-indexed positions of pattern in text.
    """
    if not pattern or not text:
        return []

    if not case_sensitive:
        text_proc = text.lower()
        pat_proc = pattern.lower()
    else:
        text_proc = text
        pat_proc = pattern

    m = len(pat_proc)
    n = len(text_proc)
    if m > n:
        return []

    # Use a delimiter character non-existent in typical hospital records
    concat_s = pat_proc + "$" + text_proc
    z = compute_z_array(concat_s)

    matches = []
    # In concat_s, text starts at index m + 1
    for i in range(m + 1, len(concat_s)):
        if z[i] == m:
            matches.append(i - (m + 1))

    return matches
