"""
Universal Hashing Module for O(1) Expected Patient ID Lookup.
Implements Universal Hash Family: h_{a,b}(k) = ((a * k + b) mod p) mod m.
Where p is a prime > N (default p = 10000019), 1 <= a < p, 0 <= b < p.
Provides separate chaining collision handling with collision metrics.
"""

import random
from typing import List, Dict, Any, Optional, Tuple

class UniversalHashTable:
    """
    Universal Hash Table for Patient Record Indexing.
    Guarantees O(1) expected lookup time for Patient IDs.
    """
    PRIME_DEFAULT = 10000019  # Large prime number

    def __init__(self, capacity: int = 10007, prime: int = PRIME_DEFAULT, seed: Optional[int] = 42):
        self.capacity = capacity
        self.prime = prime
        
        # Pick random hash family coefficients a and b
        rng = random.Random(seed) if seed is not None else random.Random()
        self.a = rng.randint(1, self.prime - 1)
        self.b = rng.randint(0, self.prime - 1)

        # Chaining table: array of buckets (list of (key, value) pairs)
        self.buckets: List[List[Tuple[str, Any]]] = [[] for _ in range(self.capacity)]
        self.num_elements = 0
        self.total_collisions = 0

    def _convert_key_to_int(self, key: str) -> int:
        """
        Converts string key (e.g. 'PAT-10042' or patient name) to integer k.
        """
        # If PAT-12345 format, extract numeric part
        clean_k = key.upper().replace("PAT-", "").replace("PAT", "").strip()
        if clean_k.isdigit():
            return int(clean_k)
        
        # Otherwise use polynomial rolling hash for string to int conversion
        h = 0
        p_pow = 1
        prime_str = 31
        for char in key:
            h = (h + ord(char) * p_pow) % self.prime
            p_pow = (p_pow * prime_str) % self.prime
        return h

    def hash_function(self, key: str) -> int:
        """
        Applies Universal Hash Function: h_{a,b}(k) = ((a * k + b) mod p) mod m
        """
        k = self._convert_key_to_int(key)
        return ((self.a * k + self.b) % self.prime) % self.capacity

    def insert(self, key: str, value: Any) -> None:
        """
        Inserts key-value pair into hash table.
        """
        idx = self.hash_function(key)
        bucket = self.buckets[idx]

        # Check if key already exists (update)
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        # Collision occurred if bucket already contained elements
        if len(bucket) > 0:
            self.total_collisions += 1

        bucket.append((key, value))
        self.num_elements += 1

    def get(self, key: str) -> Optional[Any]:
        """
        Looks up value by key in O(1) expected time.
        """
        idx = self.hash_function(key)
        bucket = self.buckets[idx]

        for k, v in bucket:
            if k == key:
                return v
        return None

    def delete(self, key: str) -> bool:
        """
        Deletes key-value pair from hash table.
        """
        idx = self.hash_function(key)
        bucket = self.buckets[idx]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.num_elements -= 1
                return True
        return False

    def get_collision_stats(self) -> Dict[str, Any]:
        """
        Returns collision and performance metrics for the hash table.
        """
        chain_lengths = [len(b) for b in self.buckets]
        max_chain = max(chain_lengths) if chain_lengths else 0
        occupied_buckets = sum(1 for b in self.buckets if len(b) > 0)
        load_factor = round(self.num_elements / max(1, self.capacity), 4)

        return {
            "capacity": self.capacity,
            "total_elements": self.num_elements,
            "occupied_buckets": occupied_buckets,
            "load_factor": load_factor,
            "total_collisions": self.total_collisions,
            "max_chain_length": max_chain,
            "hash_parameters": {"a": self.a, "b": self.b, "p": self.prime},
            "theoretical_complexity": "O(1) Expected Time"
        }
