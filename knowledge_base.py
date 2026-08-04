import os
import json
import re
import math
from typing import List, Dict, Any, Tuple

class SimpleTFIDFVectorizer:
    """
    Lightweight, self-contained TF-IDF Vectorizer built with Python standard library
    and math to ensure 100% offline compatibility without requiring external heavy packages.
    """
    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.documents_tf: List[Dict[str, float]] = []

    def _tokenize(self, text: str) -> List[str]:
        # Clean text, lowercase, extract alphanumeric tokens and common academic terms
        clean_text = re.sub(r'[^\w\s\-\.\%\$\+]', ' ', text.lower())
        tokens = [t.strip() for t in clean_text.split() if len(t.strip()) > 1]
        return tokens

    def fit_transform(self, docs: List[str]) -> List[Dict[str, float]]:
        self.vocabulary = {}
        self.idf = {}
        self.documents_tf = []
        
        doc_count = len(docs)
        if doc_count == 0:
            return []

        doc_tokens_list = [self._tokenize(doc) for doc in docs]
        
        # Build vocabulary & Document Frequencies
        df: Dict[str, int] = {}
        for tokens in doc_tokens_list:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                df[token] = df.get(token, 0) + 1
        
        vocab_idx = 0
        for token, count in df.items():
            self.vocabulary[token] = vocab_idx
            vocab_idx += 1
            # Smoothing IDF
            self.idf[token] = math.log((1 + doc_count) / (1 + count)) + 1.0

        # Calculate TF-IDF vectors (represented as sparse dicts token->tfidf)
        tfidf_vectors = []
        for tokens in doc_tokens_list:
            tf_dict: Dict[str, float] = {}
            total_tokens = max(len(tokens), 1)
            for t in tokens:
                tf_dict[t] = tf_dict.get(t, 0.0) + 1.0
            
            tfidf_vec: Dict[str, float] = {}
            norm_sq = 0.0
            for t, count in tf_dict.items():
                tf = count / total_tokens
                idf_val = self.idf.get(t, 1.0)
                val = tf * idf_val
                tfidf_vec[t] = val
                norm_sq += val * val
            
            # L2 Normalize
            norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
            for t in tfidf_vec:
                tfidf_vec[t] /= norm
                
            tfidf_vectors.append(tfidf_vec)
            self.documents_tf.append(tfidf_vec)
            
        return tfidf_vectors

    def transform_query(self, query: str) -> Dict[str, float]:
        tokens = self._tokenize(query)
        if not tokens:
            return {}
        
        tf_dict: Dict[str, float] = {}
        total_tokens = len(tokens)
        for t in tokens:
            tf_dict[t] = tf_dict.get(t, 0.0) + 1.0
            
        query_vec: Dict[str, float] = {}
        norm_sq = 0.0
        for t, count in tf_dict.items():
            if t in self.vocabulary:
                tf = count / total_tokens
                idf_val = self.idf.get(t, 1.0)
                val = tf * idf_val
                query_vec[t] = val
                norm_sq += val * val
                
        norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        for t in query_vec:
            query_vec[t] /= norm
            
        return query_vec


class KnowledgeBase:
    """
    RAG Module for EduTrust AI. Loads academic regulations, course catalog, FAQs,
    and custom documents. Performs vector similarity search with metadata filtering
    and confidence/groundedness scoring.
    """
    def __init__(self, data_dir: str = "/working_dir/c_608c0f17e2e78757/edutrust_ai/data"):
        self.data_dir = data_dir
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer = SimpleTFIDFVectorizer()
        self.tfidf_vectors: List[Dict[str, float]] = []
        self.is_indexed = False
        
        self.load_all_data()

    def load_all_data(self):
        """Loads and processes all default datasets."""
        self.chunks = []
        
        # 1. Academic Regulations
        reg_path = os.path.join(self.data_dir, "academic_regulations.json")
        if os.path.exists(reg_path):
            with open(reg_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                university = data.get("university_name", "University")
                for item in data.get("regulations", []):
                    title = item.get("title", "Regulation")
                    category = item.get("category", "Policy")
                    content = item.get("content", "")
                    text = f"University Policy [{category}]: {title}. {content}"
                    self.chunks.append({
                        "id": f"reg_{len(self.chunks)}",
                        "title": title,
                        "category": category,
                        "source": "Academic Regulations",
                        "content": content,
                        "full_text": text
                    })

        # 2. Course Catalog
        cat_path = os.path.join(self.data_dir, "course_catalog.json")
        if os.path.exists(cat_path):
            with open(cat_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("courses", []):
                    code = item.get("code", "")
                    title = item.get("title", "")
                    credits = item.get("credits", "")
                    prereqs = item.get("prerequisites", "")
                    instructor = item.get("instructor", "")
                    syllabus = item.get("syllabus", "")
                    dept = item.get("department", "")
                    sem = item.get("semester", "")
                    text = (f"Course {code}: {title} ({credits} credits, Dept: {dept}). Offered: {sem}. "
                            f"Prerequisites: {prereqs}. Instructor: {instructor}. Syllabus: {syllabus}")
                    self.chunks.append({
                        "id": f"course_{code}",
                        "title": f"{code} - {title}",
                        "category": "Course Catalog",
                        "source": f"Course Catalog ({code})",
                        "content": text,
                        "full_text": text,
                        "course_code": code,
                        "prerequisites": prereqs
                    })

        # 3. Student FAQs
        faq_path = os.path.join(self.data_dir, "student_faqs.txt")
        if os.path.exists(faq_path):
            with open(faq_path, 'r', encoding='utf-8') as f:
                content = f.read()
                qa_blocks = content.strip().split("\n\n")
                for block in qa_blocks:
                    if block.strip():
                        lines = block.strip().split("\n")
                        q_text = lines[0] if len(lines) > 0 else ""
                        a_text = " ".join(lines[1:]) if len(lines) > 1 else block
                        title = q_text.replace("Q:", "").strip()
                        self.chunks.append({
                            "id": f"faq_{len(self.chunks)}",
                            "title": title or "Student FAQ",
                            "category": "Student FAQs",
                            "source": "Student FAQs",
                            "content": block.strip(),
                            "full_text": f"Frequently Asked Question: {q_text} Answer: {a_text}"
                        })

        self.reindex()

    def add_custom_document(self, title: str, content: str, category: str = "Custom Upload", source: str = "User Document"):
        """Adds a custom document or text passage to the knowledge base."""
        # Simple paragraph or sentence chunking if content is long
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 20]
        if not paragraphs:
            paragraphs = [content.strip()]
            
        for idx, p in enumerate(paragraphs):
            chunk_title = f"{title} (Part {idx+1})" if len(paragraphs) > 1 else title
            self.chunks.append({
                "id": f"custom_{len(self.chunks)}",
                "title": chunk_title,
                "category": category,
                "source": source,
                "content": p,
                "full_text": f"{chunk_title} [{category}]: {p}"
            })
            
        self.reindex()

    def reindex(self):
        """Builds TF-IDF index over all document chunks."""
        docs = [c["full_text"] for c in self.chunks]
        self.tfidf_vectors = self.vectorizer.fit_transform(docs)
        self.is_indexed = True

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Computes dot product of normalized sparse vectors."""
        if not vec1 or not vec2:
            return 0.0
        # Iterate over smaller dict
        if len(vec1) > len(vec2):
            vec1, vec2 = vec2, vec1
        score = 0.0
        for token, val1 in vec1.items():
            if token in vec2:
                score += val1 * vec2[token]
        return score

    def search(self, query: str, top_k: int = 3, score_threshold: float = 0.10) -> List[Dict[str, Any]]:
        """
        Searches the knowledge base using vector similarity + keyword exact matching.
        Returns top_k matches sorted by relevance score.
        """
        if not self.is_indexed or not self.chunks:
            return []

        query_vec = self.vectorizer.transform_query(query)
        q_tokens = set(self.vectorizer._tokenize(query))
        
        results = []
        for idx, chunk in enumerate(self.chunks):
            doc_vec = self.tfidf_vectors[idx]
            sim_score = self._cosine_similarity(query_vec, doc_vec)
            
            # Keyword boosting for exact matches (e.g. course codes CS101, GPA, attendance numbers)
            content_lower = chunk["full_text"].lower()
            keyword_boost = 0.0
            for token in q_tokens:
                if len(token) >= 3 and token in content_lower:
                    keyword_boost += 0.08
                if len(token) >= 5 and token in content_lower:
                    keyword_boost += 0.12

            final_score = min(1.0, sim_score + keyword_boost)
            
            if final_score >= score_threshold:
                result_item = dict(chunk)
                result_item["score"] = round(final_score, 4)
                results.append(result_item)

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def compute_groundedness(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> float:
        """
        Computes RAG groundedness / factual confidence score (0.0 to 1.0).
        Evaluates how well the top retrieved documents cover the key terms in the query.
        """
        if not retrieved_docs:
            return 0.0

        top_score = retrieved_docs[0]["score"] if retrieved_docs else 0.0
        q_tokens = [t for t in self.vectorizer._tokenize(query) if len(t) > 2]
        
        if not q_tokens:
            return top_score

        # Check coverage of query terms in top docs
        combined_text = " ".join([d["full_text"].lower() for d in retrieved_docs[:2]])
        covered_count = sum(1 for t in q_tokens if t in combined_text)
        coverage_ratio = covered_count / len(q_tokens)
        
        # Groundedness combines vector similarity score and key token coverage
        groundedness = (0.6 * top_score) + (0.4 * coverage_ratio)
        return round(min(1.0, max(0.0, groundedness)), 3)

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Returns all chunks for knowledge base inspection."""
        return self.chunks


if __name__ == "__main__":
    kb = KnowledgeBase()
    print(f"Loaded {len(kb.chunks)} knowledge chunks.")
    test_queries = [
        "What is the attendance requirement?",
        "Can I drop CS101 in week 4?",
        "What are the prerequisites for AI401?",
        "How much is the merit scholarship?",
        "What is quantum teleportation rocket physics?" # Out of domain
    ]
    for q in test_queries:
        res = kb.search(q, top_k=2)
        score = kb.compute_groundedness(q, res)
        print(f"\nQuery: '{q}' | Groundedness: {score}")
        if res:
            print(f"  Top Match [{res[0]['score']}]: {res[0]['title']} -> {res[0]['content'][:80]}...")
        else:
            print("  No relevant documents found.")
