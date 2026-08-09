import math
import re
from typing import List, Dict, Any, Tuple

class SimilarityEngine:
    """
    Deduplication engine using TF-IDF cosine similarity fallback.
    Prevents publishing repetitive or previously covered research concepts.
    """
    def tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', text)]

    def compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        tf = {}
        total = len(tokens)
        if total == 0:
            return tf
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1.0
        for t in tf:
            tf[t] /= total
        return tf

    def cosine_similarity(self, text1: str, text2: str) -> float:
        t1 = self.tokenize(text1)
        t2 = self.tokenize(text2)
        
        if not t1 or not t2:
            return 0.0

        tf1 = self.compute_tf(t1)
        tf2 = self.compute_tf(t2)

        all_words = set(tf1.keys()).union(set(tf2.keys()))
        
        dot_product = sum(tf1.get(w, 0.0) * tf2.get(w, 0.0) for w in all_words)
        mag1 = math.sqrt(sum(v**2 for v in tf1.values()))
        mag2 = math.sqrt(sum(v**2 for v in tf2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def is_duplicate(self, candidate_title: str, candidate_url: str, past_memories: List[Dict[str, Any]], threshold: float = 0.65) -> Tuple[bool, str]:
        for mem in past_memories:
            past_key = mem.get("topic_key", "")
            # 1. URL exact match check
            if candidate_url and candidate_url == mem.get("source_url", ""):
                return True, f"Exact URL match with previously published topic: '{past_key}'"
            
            # 2. Text Cosine Similarity check
            sim = self.cosine_similarity(candidate_title, past_key)
            if sim >= threshold:
                return True, f"High semantic similarity ({round(sim*100, 1)}%) with past topic: '{past_key}'"

        return False, ""

similarity_engine = SimilarityEngine()
