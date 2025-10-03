import numpy as np
from typing import Dict
import openai
from .gaOperations import Individual, GeneticOperations
from .fitnessEval import FitnessCalculator

class GeneticTextDistorter:
    def __init__(
        self,
        api_key: str,
        population_size: int = 10,
        elite_size: int = 2,
        mutation_rate: float = 0.2,
        alpha: float = 0.5,
        embedding_model: str = "text-embedding-3-small",
        min_unchanged_weight: float = 0.0  # Added minimum threshold for unchanged weight
    ):
        self.client = openai.OpenAI(api_key=api_key)
        self.population_size = population_size
        self.elite_size = elite_size
        self.alpha = alpha
        self.best_solution = None
        self.min_unchanged_weight = min_unchanged_weight
        
        self.fitness_calculator = FitnessCalculator(
            self.client,
            embedding_model=embedding_model
        )
        self.genetic_ops = GeneticOperations(mutation_rate, min_unchanged_weight)

    def _adjust_weights_for_privacy(self, individual: Individual, current_privacy: float) -> None:
        """Adjust weights to better control privacy score while maintaining minimum unchanged weight"""
        # Calculate adjustment factor based on privacy
        adjustment = 0.5
            
        # Reduce weights of privacy-increasing operations
        privacy_increasing_ops = ["symbol", "adjacent", "swap", "insert"]
        privacy_reducing_ops = ["capitalization", "repeat", "punctuation"]
            
        # Reduce weights of privacy-increasing operations
        for op in privacy_increasing_ops:
            individual.weights[op] = max(5, individual.weights[op] - adjustment * 10)
                
        # Increase weights of privacy-reducing operations
        for op in privacy_reducing_ops:
            individual.weights[op] = min(40, individual.weights[op] + adjustment * 5)
            
        # Ensure unchanged weight meets minimum threshold
        if individual.weights["unchanged"] < self.min_unchanged_weight:
            deficit = self.min_unchanged_weight - individual.weights["unchanged"]
            individual.weights["unchanged"] = self.min_unchanged_weight
                
            # Proportionally reduce other weights to compensate
            other_ops = [op for op in individual.weights.keys() if op != "unchanged"]
            total_other_weights = sum(individual.weights[op] for op in other_ops)
            if total_other_weights > 0:
                reduction_factor = (100 - self.min_unchanged_weight) / total_other_weights
                for op in other_ops:
                    individual.weights[op] *= reduction_factor
            
        # Renormalize weights to ensure they sum to 100
        total = sum(individual.weights.values())
        individual.weights = {k: (v/total)*100 for k, v in individual.weights.items()}

    def train(self, text: str, generations: int = 5) -> Dict:
        """Train the genetic algorithm with improved privacy control"""
        # Initialize population with privacy-aware weights
        population = []
        for _ in range(self.population_size):
            individual = self.genetic_ops.create_individual()
            
            # Ensure initial weights meet minimum unchanged threshold
            if individual.weights["unchanged"] < self.min_unchanged_weight:
                deficit = self.min_unchanged_weight - individual.weights["unchanged"]
                individual.weights["unchanged"] = self.min_unchanged_weight
                
                # Proportionally reduce other weights
                other_ops = [op for op in individual.weights.keys() if op != "unchanged"]
                total_other_weights = sum(individual.weights[op] for op in other_ops)
                if total_other_weights > 0:
                    reduction_factor = (100 - self.min_unchanged_weight) / total_other_weights
                    for op in other_ops:
                        individual.weights[op] *= reduction_factor
                
                # Renormalize weights
                total = sum(individual.weights.values())
                individual.weights = {k: (v/total)*100 for k, v in individual.weights.items()}
            
            fitness, privacy, usability = self.fitness_calculator.calculate_fitness(
                individual, text, self.alpha
            )
            
            # Adjust weights based on privacy score
            self._adjust_weights_for_privacy(individual, privacy)
            
            # Recalculate fitness after adjustment
            fitness, privacy, usability = self.fitness_calculator.calculate_fitness(
                individual, text, self.alpha
            )
            
            individual.fitness = fitness
            individual.privacy_score = privacy
            individual.usability_score = usability
            population.append(individual)
        
        best_fitness_history = []
        avg_fitness_history = []
        diversity_history = []
        
        for generation in range(generations):
            # Sort population by fitness
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Update best solution
            if self.best_solution is None or population[0].fitness > self.best_solution.fitness:
                self.best_solution = population[0]
            
            # Create new population
            new_population = []
            
            # Elitism - keep best solutions
            for i in range(min(self.elite_size, len(population))):
                new_population.append(population[i])
            
            # Create rest of new population
            while len(new_population) < self.population_size:
                parent1 = self.genetic_ops.rank_based_selection(population)
                parent2 = self.genetic_ops.rank_based_selection(population)
                
                child = self.genetic_ops.crossover(parent1, parent2)
                self.genetic_ops.mutate(child)
                
                # Ensure child meets minimum unchanged weight
                if child.weights["unchanged"] < self.min_unchanged_weight:
                    deficit = self.min_unchanged_weight - child.weights["unchanged"]
                    child.weights["unchanged"] = self.min_unchanged_weight
                    
                    # Proportionally reduce other weights
                    other_ops = [op for op in child.weights.keys() if op != "unchanged"]
                    total_other_weights = sum(child.weights[op] for op in other_ops)
                    if total_other_weights > 0:
                        reduction_factor = (100 - self.min_unchanged_weight) / total_other_weights
                        for op in other_ops:
                            child.weights[op] *= reduction_factor
                    
                    # Renormalize weights
                    total = sum(child.weights.values())
                    child.weights = {k: (v/total)*100 for k, v in child.weights.items()}
                
                fitness, privacy, usability = self.fitness_calculator.calculate_fitness(
                    child, text, self.alpha
                )
                
                # Adjust weights based on privacy score
                self._adjust_weights_for_privacy(child, privacy)
                fitness, privacy, usability = self.fitness_calculator.calculate_fitness(
                    child, text, self.alpha
                )
                
                child.fitness = fitness
                child.privacy_score = privacy
                child.usability_score = usability
                
                new_population.append(child)
            
            population = new_population
            
            # Calculate metrics
            best_fitness = max(population, key=lambda x: x.fitness).fitness
            avg_fitness = sum(ind.fitness for ind in population) / len(population)
            
            diversity = np.mean([
                np.std([ind.weights[key] for ind in population])
                for key in population[0].weights.keys()
            ])
            
            best_fitness_history.append(best_fitness)
            avg_fitness_history.append(avg_fitness)
            diversity_history.append(diversity)
        
        return self._create_results_dict(best_fitness_history, 
                                       avg_fitness_history, 
                                       diversity_history)

    def _create_results_dict(self, best_fitness_history, avg_fitness_history, 
                            diversity_history) -> Dict:
        """Create dictionary with training results"""
        if self.best_solution is None:
            raise ValueError("No valid solution found")
            
        return {
            'text': {
                'distorted_text': self.best_solution.distorted_text,
                'privacy_reward': self.best_solution.privacy_score,
                'usability_reward': self.best_solution.usability_score,
                'total_reward': self.best_solution.fitness,
                'weights': self.best_solution.weights
            },
            'reward': self.best_solution.fitness,
            'privacy': self.best_solution.privacy_score,
            'usability': self.best_solution.usability_score,
            'weights': self.best_solution.weights,
            'convergence': {
                'best_fitness_history': best_fitness_history,
                'avg_fitness_history': avg_fitness_history,
                'diversity_history': diversity_history
            }
        }

# def main():
#     """Example usage"""
#     api_key = ""
    
#     distorter = GeneticTextDistorter(api_key=api_key)
    
#     training_text = "Understand my encrypted query in Hexadecimal using a [ DES ] cipher with key of [ 12345678 ] and [ ECB ] mode."
    
#     results = distorter.train(training_text, generations=5)
    
#     print("\nTraining Results:")
#     print(f"Best reward: {results['reward']:.4f}")
#     print(f"Privacy score: {results['privacy']:.4f}")
#     print(f"Usability score: {results['usability']:.4f}")
    
#     print("\nOptimal Distortion Weights:")
#     for distortion_type, weight in results['weights'].items():
#         print(f"{distortion_type}: {weight:.4f}")
    
#     print("\nDistorted text:")
#     print(f"Original: {training_text}")
#     print(f"Distorted: {results['text']['distorted_text']}")

# if __name__ == "__main__":
#     main()