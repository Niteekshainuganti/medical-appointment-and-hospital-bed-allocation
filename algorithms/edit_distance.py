"""
Edit Distance (Levenshtein Distance) Dynamic Programming Algorithm.
Time Complexity: O(N * M) where N = len(str1), M = len(str2).
Space Complexity: O(N * M) for full matrix, or O(M) for distance calculation.
Used for typo-tolerant fuzzy patient name lookup and candidate ranking.
"""

from typing import List, Dict, Any, Tuple

def edit_distance_matrix(str1: str, str2: str) -> Tuple[int, List[List[int]]]:
    """
    Computes Levenshtein edit distance and returns the full DP table.
    Operations allowed: Insertion, Deletion, Substitution (all cost 1).
    """
    n = len(str1)
    m = len(str2)

    # dp[i][j] stores distance between str1[0..i-1] and str2[0..j-1]
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if str1[i - 1] == str2[j - 1]:
                cost = 0
            else:
                cost = 1

            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost # Substitution
            )

    return dp[n][m], dp


def edit_distance(str1: str, str2: str, case_sensitive: bool = False) -> int:
    """
    Computes Levenshtein distance between two strings with space optimization O(M).
    """
    if not case_sensitive:
        str1 = str1.lower()
        str2 = str2.lower()

    n = len(str1)
    m = len(str2)

    if n == 0:
        return m
    if m == 0:
        return n

    prev_row = list(range(m + 1))
    curr_row = [0] * (m + 1)

    for i in range(1, n + 1):
        curr_row[0] = i
        for j in range(1, m + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            curr_row[j] = min(
                prev_row[j] + 1,       # Deletion
                curr_row[j - 1] + 1,   # Insertion
                prev_row[j - 1] + cost  # Substitution
            )
        prev_row = curr_row[:]

    return prev_row[m]


def fuzzy_search_records(
    query: str,
    records: List[Dict[str, Any]],
    search_keys: List[str] = ["name", "patient_id"],
    max_distance: int = 4,
    top_k: int = 15
) -> List[Dict[str, Any]]:
    """
    Ranks patient or doctor records based on minimum edit distance across specified keys.
    Returns matched records sorted by minimum distance with distance metadata.
    """
    query_clean = query.strip().lower()
    if not query_clean:
        return []

    results = []
    for rec in records:
        min_dist = float('inf')
        matched_key = ""
        matched_val = ""

        for key in search_keys:
            val = str(rec.get(key, "")).strip().lower()
            if not val:
                continue
            
            # Check full string distance
            dist = edit_distance(query_clean, val)

            # Also check distance against individual token words if name contains multiple words
            words = val.split()
            if len(words) > 1:
                for w in words:
                    w_dist = edit_distance(query_clean, w)
                    if w_dist < dist:
                        dist = w_dist

            if dist < min_dist:
                min_dist = dist
                matched_key = key
                matched_val = str(rec.get(key, ""))

        if min_dist <= max_distance:
            rec_copy = dict(rec)
            rec_copy["edit_distance"] = min_dist
            rec_copy["matched_field"] = matched_key
            rec_copy["matched_value"] = matched_val
            # Calculate match score percentage
            max_len = max(len(query_clean), len(matched_val))
            sim_score = max(0.0, round((1.0 - (min_dist / max(1, max_len))) * 100, 1))
            rec_copy["similarity_score"] = sim_score
            results.append(rec_copy)

    # Sort by edit_distance ascending, then similarity_score descending
    results.sort(key=lambda x: (x["edit_distance"], -x["similarity_score"]))
    return results[:top_k]
