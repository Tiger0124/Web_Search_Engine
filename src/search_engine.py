"""Search engine module for processing queries and ranking results."""

import math
from collections import defaultdict
from typing import Dict, List, Tuple

from .indexer import Indexer
from .utils import tokenize


class SearchEngine:
    """Search engine for processing queries and returning ranked results."""
    
    def __init__(self, indexer: Indexer):
        """
        Initialize the search engine.
        
        Args:
            indexer: The indexer containing the inverted index.
        """
        self.indexer = indexer
        
        # BM25 parameters
        self.k1 = 1.5  # Term frequency saturation parameter
        self.b = 0.75  # Document length normalization parameter
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search for documents matching the query.
        
        Args:
            query: The search query.
            top_k: Number of top results to return.
            
        Returns:
            List of search results with document info and scores.
        """
        # Tokenize the query
        query_terms = tokenize(query)
        
        if not query_terms:
            return []
        
        # Calculate BM25 scores for each document
        doc_scores: Dict[int, float] = defaultdict(float)
        
        num_docs = len(self.indexer.documents)
        avg_doc_len = self.indexer.avg_doc_length
        
        for term in query_terms:
            postings = self.indexer.get_postings(term)
            
            if not postings:
                continue
            
            # Calculate IDF for the term
            df = len(postings)
            idf = math.log((num_docs - df + 0.5) / (df + 0.5) + 1)
            
            for doc_id, _ in postings:
                # Get term frequency from posting
                doc_len = self.indexer.doc_lengths.get(doc_id, 1)
                
                # Calculate BM25 score component
                # We need the raw term frequency, which we'll approximate
                tf = 1  # Simplified: assume tf=1 for presence
                
                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / avg_doc_len))
                
                score = idf * (numerator / denominator)
                doc_scores[doc_id] += score
        
        # Sort documents by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get top-k results
        results = []
        for doc_id, score in sorted_docs[:top_k]:
            doc = self.indexer.get_document(doc_id)
            if doc:
                result = {
                    'url': doc.get('url', ''),
                    'title': doc.get('title', 'Untitled'),
                    'content': doc.get('content', '')[:200] + '...',  # Snippet
                    'score': round(score, 4)
                }
                results.append(result)
        
        return results
    
    def search_boolean(self, query: str, operator: str = 'AND') -> List[Dict]:
        """
        Perform boolean search with AND/OR operators.
        
        Args:
            query: The search query.
            operator: Boolean operator ('AND' or 'OR').
            
        Returns:
            List of matching documents.
        """
        query_terms = tokenize(query)
        
        if not query_terms:
            return []
        
        result_docs = None
        
        for term in query_terms:
            postings = self.indexer.get_postings(term)
            term_docs = set(doc_id for doc_id, _ in postings)
            
            if result_docs is None:
                result_docs = term_docs
            elif operator.upper() == 'AND':
                result_docs = result_docs.intersection(term_docs)
            else:  # OR
                result_docs = result_docs.union(term_docs)
        
        if result_docs is None:
            return []
        
        # Get document details
        results = []
        for doc_id in result_docs:
            doc = self.indexer.get_document(doc_id)
            if doc:
                result = {
                    'url': doc.get('url', ''),
                    'title': doc.get('title', 'Untitled'),
                    'content': doc.get('content', '')[:200] + '...'
                }
                results.append(result)
        
        return results
    
    def get_suggestions(self, prefix: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on prefix matching.
        
        Args:
            prefix: The prefix to match.
            limit: Maximum number of suggestions.
            
        Returns:
            List of suggested terms.
        """
        prefix = prefix.lower()
        suggestions = []
        
        for term in self.indexer.inverted_index.keys():
            if term.startswith(prefix):
                suggestions.append(term)
                if len(suggestions) >= limit:
                    break
        
        return suggestions
