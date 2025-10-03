from dataclasses import dataclass
import random
from typing import Dict, List

@dataclass
class Individual:
    """Represents a single solution in the genetic algorithm"""
    weights: Dict[str, float]
    fitness: float = 0.0
    privacy_score: float = 0.0
    usability_score: float = 0.0
    distorted_text: str = ""

class GeneticOperations:
    def __init__(self, mutation_rate: float = 0.2, min_unchanged_weight: float = 30.0):
        self.mutation_rate = mutation_rate
        self.min_unchanged_weight = min_unchanged_weight

    def _normalize_weights_with_minimum(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize weights while ensuring minimum unchanged weight"""
        # First ensure unchanged meets minimum
        if weights["unchanged"] < self.min_unchanged_weight:
            weights["unchanged"] = self.min_unchanged_weight
            
            # Adjust other weights proportionally
            other_ops = [op for op in weights.keys() if op != "unchanged"]
            remaining_weight = 100 - self.min_unchanged_weight
            total_other_weights = sum(weights[op] for op in other_ops)
            
            if total_other_weights > 0:
                scale_factor = remaining_weight / total_other_weights
                for op in other_ops:
                    weights[op] *= scale_factor
        
        # Normalize to ensure sum is 100
        total = sum(weights.values())
        return {k: (v/total)*100 for k, v in weights.items()}

    def create_individual(self) -> Individual:
        """Create a random individual with normalized weights and minimum unchanged weight"""
        weights = {
            "unchanged": max(random.random(), self.min_unchanged_weight/100),
            "capitalization": random.random(),
            "symbol": random.random(),
            "adjacent": random.random(),
            "swap": random.random(),
            "insert": random.random(),
            "repeat": random.random(),
            "punctuation": random.random()
        }
        
        normalized_weights = self._normalize_weights_with_minimum(weights)
        return Individual(weights=normalized_weights)

    def rank_based_selection(self, population: List[Individual]) -> Individual:
        """Select individual using tournament selection"""
        tournament = random.sample(population, 3)
        return max(tournament, key=lambda x: x.fitness)

    def crossover(self, parent1: Individual, parent2: Individual) -> Individual:
        """Create child using uniform crossover while maintaining minimum unchanged weight"""
        child_weights = {}
        
        # Special handling for unchanged weight
        if parent1.weights["unchanged"] >= self.min_unchanged_weight and parent2.weights["unchanged"] >= self.min_unchanged_weight:
            # Both parents meet minimum - normal crossover for unchanged
            child_weights["unchanged"] = parent1.weights["unchanged"] if random.random() < 0.5 else parent2.weights["unchanged"]
        else:
            # At least one parent doesn't meet minimum - use minimum
            child_weights["unchanged"] = self.min_unchanged_weight
        
        # Normal crossover for other weights
        for key in parent1.weights:
            if key != "unchanged":
                if random.random() < 0.5:
                    child_weights[key] = parent1.weights[key]
                else:
                    child_weights[key] = parent2.weights[key]
        
        # Normalize while maintaining minimum unchanged weight
        normalized_weights = self._normalize_weights_with_minimum(child_weights)
        return Individual(weights=normalized_weights)

    def mutate(self, individual: Individual) -> None:
        """Enhanced mutation while maintaining minimum unchanged weight"""
        if random.random() < self.mutation_rate:
            # Choose random weight to mutate, excluding unchanged if it would go below minimum
            mutable_keys = list(individual.weights.keys())
            if individual.weights["unchanged"] <= self.min_unchanged_weight:
                mutable_keys.remove("unchanged")
                
            if mutable_keys:  # Only mutate if we have mutable weights
                key_to_mutate = random.choice(mutable_keys)
                individual.weights[key_to_mutate] = random.uniform(0, 100)
                
                # Normalize while maintaining minimum unchanged weight
                individual.weights = self._normalize_weights_with_minimum(individual.weights)