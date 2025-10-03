import numpy as np
from typing import Tuple
from openai import OpenAI
from .gaOperations import Individual
from .distortionFuntions import distort_text

class FitnessCalculator:
    def __init__(self, client: OpenAI, 
                 embedding_model: str = "text-embedding-3-small"):
        self.client = client
        self.embedding_model = embedding_model
        
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using OpenAI's API"""
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return np.array(response.data[0].embedding)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def calculate_privacy_score(self, original_text: str, distorted_text: str) -> float:
        """Calculate privacy score using embeddings"""
        original_embedding = self.get_embedding(original_text)
        distorted_embedding = self.get_embedding(distorted_text)
        
        return 1 - self.cosine_similarity(original_embedding, distorted_embedding)
    
    def compare_words(self, original, modified):
        matches = sum(1 for i in range(len(original)) if i < len(modified) and original[i] == modified[i])
        total = len(original)
        return matches / total

    def get_usability_score(self, original_text: str, distorted_text: str) -> float:
        """Calculate usability score using GPT model"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Reconstruct the distorted paragraph exactly as it should be. Respond with only the corrected paragraph and nothing else."},
                    # {"role": "system", "content": "Recover the distorted hexadecimal key provided. Respond with the recovered key only and nothing else."},
                    {"role": "user", "content": distorted_text}
                ],
                temperature=0,
                max_tokens=100
            )
            
            gpt_answer = response.choices[0].message.content.lower().strip()
            
            words1 = set(original_text.lower().split())
            words2 = set(gpt_answer.lower().split())
            
            if not words1:
                return 0.0
                
            matching_words = words1.intersection(words2)
            return len(matching_words) / len(words1)
            
        except Exception as e:
            print(f"Error getting GPT response: {e}")
            return 0.0

    def calculate_fitness(self, individual: Individual, text: str, alpha: float) -> Tuple[float, float, float]:
        """Calculate fitness based on privacy and usability scores"""
        distorted_text = distort_text(text, individual.weights)
        individual.distorted_text = distorted_text
        
        privacy_score = self.calculate_privacy_score(text, distorted_text)
        usability_score = self.get_usability_score(text, distorted_text)
        
        # Calculate fitness as weighted sum of privacy and usability
        fitness = (alpha * privacy_score) + ((1 - alpha) * usability_score)
        
        return fitness, privacy_score, usability_score