"""Indexer module for building inverted index."""

import math
import pickle
from collections import defaultdict
from typing import Dict, List, Tuple

from .utils import tokenize


class Indexer:
    """Builds and manages the inverted index for search."""
    
    def __init__(self):
        """Initialize the indexer."""
        self.inverted_index: Dict[str, List[Tuple[int, float]]] = defaultdict(list)
        self.documents: List[Dict] = []
        self.doc_lengths: Dict[int, int] = {}
        self.avg_doc_length: float = 0.0
        
    def build_index(self, documents: List[Dict]) -> None:
        """
        Build the inverted index from a list of documents.
        
        Args:
            documents: List of document dictionaries with 'url', 'title', 'content'.
        """
        self.documents = documents
        self.inverted_index = defaultdict(list)
        
        # First pass: tokenize all documents and calculate document lengths
        doc_tokens: List[List[str]] = []
        total_length = 0
        
        for doc_id, doc in enumerate(documents):
            # Combine title and content for indexing
            text = f"{doc.get('title', '')} {doc.get('content', '')}"
            tokens = tokenize(text)
            doc_tokens.append(tokens)
            self.doc_lengths[doc_id] = len(tokens)
            total_length += len(tokens)
        
        # Calculate average document length
        if documents:
            self.avg_doc_length = total_length / len(documents)
        
        # Second pass: build the inverted index with TF-IDF scores
        # Calculate document frequency for each term
        doc_freq: Dict[str, int] = defaultdict(int)
        for tokens in doc_tokens:
            unique_terms = set(tokens)
            for term in unique_terms:
                doc_freq[term] += 1
        
        # Build the index
        num_docs = len(documents)
        for doc_id, tokens in enumerate(doc_tokens):
            # Calculate term frequency for this document
            term_freq: Dict[str, int] = defaultdict(int)
            for token in tokens:
                term_freq[token] += 1
            
            # Calculate TF-IDF for each term
            for term, tf in term_freq.items():
                # TF: normalized by document length
                tf_normalized = tf / len(tokens) if tokens else 0
                
                # IDF: log(N / df)
                idf = math.log(num_docs / doc_freq[term]) if doc_freq[term] > 0 else 0
                
                # TF-IDF score
                tfidf = tf_normalized * idf
                
                self.inverted_index[term].append((doc_id, tfidf))
        
        # Sort posting lists by TF-IDF score (descending)
        for term in self.inverted_index:
            self.inverted_index[term].sort(key=lambda x: x[1], reverse=True)
    
    def get_postings(self, term: str) -> List[Tuple[int, float]]:
        """
        Get the posting list for a term.
        
        Args:
            term: The term to look up.
            
        Returns:
            List of (doc_id, score) tuples.
        """
        term = term.lower()
        return self.inverted_index.get(term, [])
    
    def save_index(self, filepath: str) -> None:
        """
        Save the index to a pickle file.
        
        Args:
            filepath: Path to save the index.
        """
        data = {
            'inverted_index': dict(self.inverted_index),
            'documents': self.documents,
            'doc_lengths': self.doc_lengths,
            'avg_doc_length': self.avg_doc_length
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    def load_index(self, filepath: str) -> None:
        """
        Load the index from a pickle file.
        
        Args:
            filepath: Path to the index file.
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.inverted_index = defaultdict(list, data['inverted_index'])
        self.documents = data['documents']
        self.doc_lengths = data['doc_lengths']
        self.avg_doc_length = data['avg_doc_length']
    
    def get_document(self, doc_id: int) -> Dict:
        """
        Get a document by its ID.
        
        Args:
            doc_id: The document ID.
            
        Returns:
            Document dictionary.
        """
        if 0 <= doc_id < len(self.documents):
            return self.documents[doc_id]
        return {}
