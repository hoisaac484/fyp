from typing import Dict
import random

# Keyboard adjacency for realistic typos (QWERTY layout)
keyboard_adjacent = {
    'a': ['q', 'w', 's', 'z'], 'b': ['v', 'n', 'g'], 'c': ['x', 'v', 'd'],
    'd': ['s', 'f', 'e'], 'e': ['w', 'r', 'd'], 'f': ['d', 'g', 'r'],
    'g': ['f', 'h', 't'], 'h': ['g', 'j', 'y'], 'i': ['u', 'k'],
    'j': ['h', 'k', 'u'], 'k': ['j', 'l', 'i'], 'l': ['k', 'o'],
    'm': ['n', 'j'], 'n': ['b', 'm', 'h'], 'o': ['p', 'l'],
    'p': ['o', 'l'], 'r': ['e', 't', 'f'], 's': ['a', 'd', 'w', 'x'],
    't': ['r', 'y', 'g'], 'u': ['y', 'i', 'j'], 'v': ['c', 'b', 'f'],
    'w': ['q', 'e', 's'], 'x': ['z', 'c', 's'], 'y': ['t', 'u', 'h'],
    'z': ['x', 'a']
}

# Symbol replacements
symbol_map = {
    'a': ['@', '∂'], 'b': ['ß', 'ƀ'], 'c': ['©', '¢', '('],
    'd': ['∂', 'Ð', 'đ'], 'e': ['€', '£'], 'f': ['ƒ', '#', 'ph'],
    'g': ['ğ'], 'h': ['#', '♄'], 'i': ['!', '|'],
    'j': ['¿', 'Ɉ', 'ʝ'], 'k': ['κ', '|<', 'ʞ'], 'l': [ '|', 'ł'],
    'm': ['^^', 'ɱ', '♏'], 'n': ['η', 'и', 'π'], 'o': ['()', '°'],
    'p': ['ρ', '¶', 'þ'], 'q': ['¶', '&'], 'r': ['®', 'Я', 'ɹ'],
    's': ['$', '§'], 't': ['+', '†'], 'u': ['μ', 'υ', '∪'],
    'v': ['√', '∨', 'ⱱ'], 'w': ['ω', 'ψ', 'vv'], 'x': ['×', 'χ', '><'],
    'y': ['¥', 'γ', 'ʎ'], 'z': [ 'ƶ', 'ℤ']
}

punctuation = ['!', '?', '*', '~', '.', ',', '#', '$', '%', '&']

def assign_distortions(text: str, weights: Dict[str, float]) -> list:
    """Assign distortion types to each character position based on weights"""
    char_positions = list(range(len(text)))
    assignments = []
    
    # Normalize weights to percentages if they don't sum to 100
    total_weight = sum(weights.values())
    normalized_weights = {k: (v / total_weight) * 100 for k, v in weights.items()}
    
    # First, identify capital letters and mark them as unchanged
    capital_positions = [i for i, char in enumerate(text) if char.isupper()]
    for pos in capital_positions:
        if pos in char_positions:
            char_positions.remove(pos)
            assignments.append((pos, "unchanged"))
    
    # Calculate number of positions for each distortion type on remaining characters
    remaining_positions = len(char_positions)
    for distortion_type, percentage in normalized_weights.items():
        count = int((percentage / 100) * remaining_positions)
        if count > 0 and char_positions:
            positions = random.sample(char_positions, min(count, len(char_positions)))
            assignments.extend([(pos, distortion_type) for pos in positions])
            char_positions = [pos for pos in char_positions if pos not in positions]
    
    # Assign any remaining positions as unchanged
    assignments.extend([(pos, "unchanged") for pos in char_positions])
    
    # Sort by position
    assignments.sort(key=lambda x: x[0])
    return [dist_type for _, dist_type in assignments]

def apply_distortion(char: str, distortion_type: str, context: list = None) -> str:
    """Apply a specific distortion to a character"""
    if not char.strip() or distortion_type == "unchanged":
        return char
    
    # Skip all distortions for uppercase letters
    if char.isupper():
        return char
        
    if distortion_type == "capitalization":
        return char.upper() if char.islower() else char.lower()
        
    elif distortion_type == "symbol" and char.lower() in symbol_map:
        return random.choice(symbol_map[char.lower()])
        
    elif distortion_type == "adjacent" and char.lower() in keyboard_adjacent:
        return random.choice(keyboard_adjacent[char.lower()])
        
    elif distortion_type == "repeat":
        return char * 2
        
    elif distortion_type == "insert":
        return char + random.choice("abcdefghijklmnopqrstuvwxyz")
        
    elif distortion_type == "punctuation":
        return char + random.choice(punctuation)
        
    return char

def distort_text(text: str, distortion_weights: Dict[str, float] = None) -> str:
    # Get distortion assignments for each character
    distortions = assign_distortions(text, distortion_weights)
    
    # Convert text to list for easier manipulation
    chars = list(text)
    result = []
    
    # Apply distortions
    i = 0
    while i < len(chars):
        if i >= len(distortions):
            # If we've run out of distortion assignments, just append the remaining characters
            result.append(chars[i])
            i += 1
            continue
            
        dist_type = distortions[i]
        
        # Handle swap distortion specially
        if dist_type == "swap" and i < len(chars) - 1:
            next_char = chars[i + 1]
            # Only swap if next character is not uppercase
            if not next_char.isupper():
                # Append the swapped characters to result
                result.append(next_char)
                result.append(chars[i])
                i += 2  # Skip both characters as we've handled them
                continue
            # If swap wasn't applied, fall through to normal processing
        
        # Apply normal (non-swap) distortion
        distorted_char = apply_distortion(chars[i], dist_type)
        result.append(distorted_char)
        i += 1
    
    return "".join(result)