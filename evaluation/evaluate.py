"""Evaluation module for measuring search engine performance."""

import json
import math
from typing import Dict, List, Set


def load_ground_truth(filepath: str) -> Dict[str, List[str]]:
    """
    Load ground truth data from a JSON file.
    
    Args:
        filepath: Path to the ground truth JSON file.
        
    Returns:
        Dictionary mapping queries to relevant document URLs.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """
    Calculate precision at K.
    
    Args:
        retrieved: List of retrieved document URLs in order.
        relevant: Set of relevant document URLs.
        k: Number of results to consider.
        
    Returns:
        Precision at K value.
    """
    if k <= 0:
        return 0.0
    
    retrieved_k = retrieved[:k]
    relevant_retrieved = sum(1 for url in retrieved_k if url in relevant)
    
    return relevant_retrieved / k


def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """
    Calculate recall at K.
    
    Args:
        retrieved: List of retrieved document URLs in order.
        relevant: Set of relevant document URLs.
        k: Number of results to consider.
        
    Returns:
        Recall at K value.
    """
    if not relevant:
        return 0.0
    
    retrieved_k = retrieved[:k]
    relevant_retrieved = sum(1 for url in retrieved_k if url in relevant)
    
    return relevant_retrieved / len(relevant)


def f1_score(precision: float, recall: float) -> float:
    """
    Calculate F1 score from precision and recall.
    
    Args:
        precision: Precision value.
        recall: Recall value.
        
    Returns:
        F1 score.
    """
    if precision + recall == 0:
        return 0.0
    
    return 2 * (precision * recall) / (precision + recall)


def average_precision(retrieved: List[str], relevant: Set[str]) -> float:
    """
    Calculate average precision (AP).
    
    Args:
        retrieved: List of retrieved document URLs in order.
        relevant: Set of relevant document URLs.
        
    Returns:
        Average precision value.
    """
    if not relevant:
        return 0.0
    
    precisions = []
    relevant_count = 0
    
    for i, url in enumerate(retrieved):
        if url in relevant:
            relevant_count += 1
            precision = relevant_count / (i + 1)
            precisions.append(precision)
    
    if not precisions:
        return 0.0
    
    return sum(precisions) / len(relevant)


def mean_average_precision(results: Dict[str, List[str]], 
                           ground_truth: Dict[str, List[str]]) -> float:
    """
    Calculate Mean Average Precision (MAP) across all queries.
    
    Args:
        results: Dictionary mapping queries to retrieved document URLs.
        ground_truth: Dictionary mapping queries to relevant document URLs.
        
    Returns:
        MAP value.
    """
    if not results:
        return 0.0
    
    aps = []
    for query, retrieved in results.items():
        if query in ground_truth:
            relevant = set(ground_truth[query])
            ap = average_precision(retrieved, relevant)
            aps.append(ap)
    
    if not aps:
        return 0.0
    
    return sum(aps) / len(aps)


def dcg_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """
    Calculate Discounted Cumulative Gain at K.
    
    Args:
        retrieved: List of retrieved document URLs in order.
        relevant: Set of relevant document URLs.
        k: Number of results to consider.
        
    Returns:
        DCG at K value.
    """
    dcg = 0.0
    for i, url in enumerate(retrieved[:k]):
        if url in relevant:
            # Binary relevance: rel = 1 if relevant, 0 otherwise
            rel = 1
            dcg += rel / math.log2(i + 2)  # i + 2 because we start from position 1
    
    return dcg


def ndcg_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain at K.
    
    Args:
        retrieved: List of retrieved document URLs in order.
        relevant: Set of relevant document URLs.
        k: Number of results to consider.
        
    Returns:
        NDCG at K value.
    """
    dcg = dcg_at_k(retrieved, relevant, k)
    
    # Ideal DCG: all relevant documents at the top
    ideal_retrieved = list(relevant)[:k]
    idcg = dcg_at_k(ideal_retrieved, relevant, k)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def evaluate_search_engine(search_engine, ground_truth_path: str, k: int = 10) -> Dict:
    """
    Evaluate the search engine using ground truth data.
    
    Args:
        search_engine: SearchEngine instance.
        ground_truth_path: Path to ground truth JSON file.
        k: Number of results to consider for evaluation.
        
    Returns:
        Dictionary containing evaluation metrics.
    """
    ground_truth = load_ground_truth(ground_truth_path)
    
    metrics = {
        'precision_at_k': [],
        'recall_at_k': [],
        'f1_at_k': [],
        'average_precision': [],
        'ndcg_at_k': []
    }
    
    for query, relevant_urls in ground_truth.items():
        # Get search results
        results = search_engine.search(query, top_k=k)
        retrieved_urls = [r['url'] for r in results]
        relevant_set = set(relevant_urls)
        
        # Calculate metrics
        p_at_k = precision_at_k(retrieved_urls, relevant_set, k)
        r_at_k = recall_at_k(retrieved_urls, relevant_set, k)
        f1 = f1_score(p_at_k, r_at_k)
        ap = average_precision(retrieved_urls, relevant_set)
        ndcg = ndcg_at_k(retrieved_urls, relevant_set, k)
        
        metrics['precision_at_k'].append(p_at_k)
        metrics['recall_at_k'].append(r_at_k)
        metrics['f1_at_k'].append(f1)
        metrics['average_precision'].append(ap)
        metrics['ndcg_at_k'].append(ndcg)
    
    # Calculate averages
    summary = {}
    for metric_name, values in metrics.items():
        if values:
            summary[f'avg_{metric_name}'] = sum(values) / len(values)
        else:
            summary[f'avg_{metric_name}'] = 0.0
    
    summary['map'] = summary.get('avg_average_precision', 0.0)
    
    return summary


if __name__ == '__main__':
    import sys
    import os
    
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.indexer import Indexer
    from src.search_engine import SearchEngine
    
    # Load the index
    indexer = Indexer()
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'data', 'inverted_index.pkl')
    
    if os.path.exists(index_path):
        indexer.load_index(index_path)
        
        # Create search engine
        search_engine = SearchEngine(indexer)
        
        # Evaluate
        ground_truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        
        if os.path.exists(ground_truth_path):
            results = evaluate_search_engine(search_engine, ground_truth_path)
            print("Evaluation Results:")
            print("-" * 40)
            for metric, value in results.items():
                print(f"{metric}: {value:.4f}")
        else:
            print("Ground truth file not found.")
    else:
        print("Index file not found. Please build the index first.")
