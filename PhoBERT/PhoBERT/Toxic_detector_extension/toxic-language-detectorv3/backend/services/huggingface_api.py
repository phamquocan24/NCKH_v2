# services/huggingface_api.py
import requests
from typing import Dict, Any, List, Tuple
import os

class HuggingFaceAPI:
    def __init__(self):
        self.api_url = os.getenv("HUGGINGFACE_API_URL", "https://api-inference.huggingface.co/models/")
        self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def predict(self, text: str, model_id: str = "distilbert-base-uncased-finetuned-sst-2-english") -> Tuple[int, float]:
        """
        Predict the class of the text using a HuggingFace model
        
        Args:
            text (str): The text to predict
            model_id (str): The model ID on HuggingFace Hub
        
        Returns:
            Tuple[int, float]: Predicted class and confidence
        """
        api_url = f"{self.api_url}{model_id}"
        payload = {"inputs": text}
        
        response = requests.post(api_url, headers=self.headers, json=payload)
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            # Handle classification output
            if "label" in result[0]:
                label = result[0]["label"]
                score = result[0]["score"]
                
                # Map label to our classes
                label_mapping = {
                    "POSITIVE": 0,  # clean
                    "NEGATIVE": 1,  # offensive
                    "NEUTRAL": 0,   # clean
                    "HATE": 2,      # hate
                    "SPAM": 3       # spam
                }
                
                predicted_class = label_mapping.get(label.upper(), 0)
                return predicted_class, score
        
        # Default return if unable to process
        return 0, 0.5
