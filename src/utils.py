"""Utility functions for the web search engine."""

import math
import re
import string
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing special characters and extra whitespace.
    
    Args:
        text: The input text to clean.
        
    Returns:
        Cleaned text string.
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into individual words.
    
    Args:
        text: The input text to tokenize.
        
    Returns:
        List of tokens (words).
    """
    if not text:
        return []
    
    # Clean the text first
    cleaned = clean_text(text)
    
    # Split into words
    tokens = cleaned.split()
    
    # Remove stopwords (common English words)
    stopwords = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
        'she', 'we', 'they', 'what', 'which', 'who', 'whom', 'whose',
        'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just'
    }
    
    tokens = [token for token in tokens if token not in stopwords and len(token) > 1]
    
    return tokens


def calculate_tf(term: str, document: List[str]) -> float:
    """
    Calculate term frequency (TF) for a term in a document.
    
    Args:
        term: The term to calculate TF for.
        document: List of tokens in the document.
        
    Returns:
        Term frequency value.
    """
    if not document:
        return 0.0
    
    term_count = document.count(term)
    return term_count / len(document)


def calculate_idf(term: str, documents: List[List[str]]) -> float:
    """
    Calculate inverse document frequency (IDF) for a term.
    
    Args:
        term: The term to calculate IDF for.
        documents: List of tokenized documents.
        
    Returns:
        Inverse document frequency value.
    """
    if not documents:
        return 0.0
    
    doc_count = sum(1 for doc in documents if term in doc)
    
    if doc_count == 0:
        return 0.0
    
    return math.log(len(documents) / doc_count)
