# utils/vector_utils.py
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Initialize the vectorizer
_vectorizer = None

def _get_vectorizer():
    """
    Get or initialize the TF-IDF vectorizer
    """
    global _vectorizer
    if _vectorizer is None:
        _vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    return _vectorizer

def preprocess_text(text):
    """
    Preprocess Vietnamese text for vectorization
    
    Args:
        text (str): Raw Vietnamese text
        
    Returns:
        str: Preprocessed text
    """
    # Convert to lowercase (preserving Vietnamese diacritical marks)
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # For Vietnamese text, we need to preserve diacritical marks
    # Only remove punctuation that doesn't affect meaning
    text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text)
    text = re.sub(r'\d+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Use Vietnamese-specific tokenization if available
    try:
        from underthesea import word_tokenize
        text = word_tokenize(text, format="text")
    except ImportError:
        # Fallback if underthesea is not available
        pass
    
    return text

def extract_features(text):
    """
    Extract feature vector from text
    
    Args:
        text (str): Input text
        
    Returns:
        numpy.ndarray: Feature vector
    """
    # Get vectorizer
    vectorizer = _get_vectorizer()
    
    # Preprocess text
    processed_text = preprocess_text(text)
    
    # Fit vectorizer if not trained
    if not hasattr(vectorizer, 'vocabulary_'):
        vectorizer.fit([processed_text])
    
    # Transform text to vector
    vector = vectorizer.transform([processed_text])
    
    # Return as dense array
    return vector.toarray()[0]

def compute_similarity(vec1, vec2):
    """
    Compute cosine similarity between two vectors
    
    Args:
        vec1 (numpy.ndarray): First vector
        vec2 (numpy.ndarray): Second vector
        
    Returns:
        float: Similarity score (0-1)
    """
    # Reshape vectors if needed
    if len(vec1.shape) == 1:
        vec1 = vec1.reshape(1, -1)
    if len(vec2.shape) == 1:
        vec2 = vec2.reshape(1, -1)
    
    # Compute similarity
    sim = cosine_similarity(vec1, vec2)[0][0]
    
    return float(sim)

def find_similar_vectors(query_vector, vectors, threshold=0.7, top_n=10):
    """
    Find similar vectors to a query vector
    
    Args:
        query_vector (numpy.ndarray): Query vector
        vectors (List[numpy.ndarray]): List of vectors to compare against
        threshold (float): Minimum similarity threshold
        top_n (int): Maximum number of results to return
        
    Returns:
        List[Tuple[int, float]]: List of (index, similarity) tuples
    """
    similarities = []
    
    for i, vec in enumerate(vectors):
        sim = compute_similarity(query_vector, vec)
        if sim >= threshold:
            similarities.append((i, sim))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N results
    return similarities[:top_n]