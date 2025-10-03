import binascii
from ga.gaDistorter import GeneticTextDistorter
from modules.instruction_module.instruction_encryptor import encrypt

# Assistant configurations
ASSISTANT_CONFIGS = {
    "1": {
        "name": "Approach 1: Pass encryption key and method",
        "instructions": "Decrypt the question then respond with the answer."
    },
    "2": {
        "name": "Approach 2: Pass sample plaintext and its corresponding encrypted text",
        "instructions": "A sample plaintext and its encrypted version and an encrypted question is provided. You should:\n"
                        "1. Identify the encryption method and key used.\n"
                        "2. Then use Python Crypto.Cipher to decrypt the ciphertext question which uses the same encryption method and key as sample plaintext.\n"
                        "3. Answer the encrypted question."
    },
    "3": {
        "name": "Approach 3: Pass distorted encryption key and method",
        "instructions": "A distorted text and an encrypted question is provided. You should:\n"
                        "1. Without coding, reconstruct and understand the distorted paragraph exactly as it should be.\n"
                        "2. Without coding, Convert word forms of numbers to 0-9 and phonetic alphabet to A-F. "
                        "Directly combine them into hexadecimal keys, each [] contains only 4 hexadecimal digits.\n"
                        "3. Then use python Crypto.Cipher to decrypt the encrypted question.\n"
                        "4. Lastly tell me the answer to question."
    }
}

def number_to_words(n):
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", 
            "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    if n < 20:
        return units[n]
    else:
        return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")

def hex_to_text(hex_str, words_per_group=4):
    hex_map = {
        '0': "Zero", '1': "One", '2': "Two", '3': "Three", '4': "Four",
        '5': "Five", '6': "Six", '7': "Seven", '8': "Eight", '9': "Nine",
        'A': "Alpha", 'B': "Bravo", 'C': "Charlie", 'D': "Delta",
        'E': "Echo", 'F': "Freddy"
    }
    
    hex_str = hex_str.upper()  # Ensure uppercase for consistency
    words = [hex_map[digit] for digit in hex_str]
    
    # Group words into sets of 4 inside brackets
    grouped_words = ["[ " + " ".join(words[i:i+words_per_group]) + " ]" 
                     for i in range(0, len(words), words_per_group)]
    
    return " ".join(grouped_words)

def generate_key_guide_text(method, keys):
    """Generate guide text with encryption information"""
    if method == "1":  # Caesar
        return f"Understand my encrypted query using a [ Caesar ] cipher with Key of [ {number_to_words(keys['caesar'])} ]."
    elif method == "2":  # DES
        key_hex = binascii.hexlify(keys["des"]).decode()
        return f"Understand my encrypted query using a [ DES ] cipher with key of [ {key_hex} ] and [ ECB ] mode." 
    elif method == "3":  # AES
        key_hex = binascii.hexlify(keys["aes"]["key"]).decode()
        return f"Understand my encrypted query using a [ AES ] cipher in [ CBC ] mode with key of [ {key_hex} ] and embedded initialization vector."
    elif method == "4":  # ChaCha20
        key_hex = binascii.hexlify(keys["chacha20"]["key"]).decode()
        nonce_hex = binascii.hexlify(keys["chacha20"]["nonce"]).decode()
        return f"Understand my encrypted query using a [ ChaCha20 (RFC 7539) ] cipher with key of [ {key_hex} ] and nonce of [ {nonce_hex} ]"
    else:
        return ""
    
def generate_text_key_guide_text(method, keys):
    """Generate guide text with encryption information in text format"""
    if method == "1":  # Caesar
        return f"Understand my encrypted query using a [ Caesar ] cipher with Key of [ {number_to_words(keys['caesar'])} ]."
    elif method == "2":  # DES
        key_hex = binascii.hexlify(keys["des"]).decode()
        return f"Understand my encrypted query using a [ Data Encryption Standard ] cipher in [ Electronic Code Book ] mode. Key: [ {hex_to_text(key_hex)} ]."
    elif method == "3":  # AES
        key_hex = binascii.hexlify(keys["aes"]["key"]).decode()
        return f"Understand my encrypted query using a [ Advanced Encryption Standard ] cipher in [ Cipher Block Chaining ] mode and [ PKCS7 ] Padding with Embedded Initialization Vector at the beginning of encrypted question. Key: [ {hex_to_text(key_hex)} ]."
    elif method == "4":  # ChaCha20
        key_hex = binascii.hexlify(keys["chacha20"]["key"]).decode()
        nonce_hex = binascii.hexlify(keys["chacha20"]["nonce"]).decode()
        return f"Understand my encrypted query using a [ ChaCha20 (RFC 7539) ] cipher. Key: [ {hex_to_text(key_hex)} ] and Nonce: [ {hex_to_text(nonce_hex)} ]."
    else:
        return ""

def get_assistant_configs():
    """Return the assistant configurations"""
    return ASSISTANT_CONFIGS

def generate_guide_text(assistant_approach, encryption_method, encryption_keys, min_unchanged_weight=None, api_key=None):
    """Generate guide text based on assistant approach and encryption method"""
    
    # For Approach 1, include encryption info
    if assistant_approach == "1":
        return generate_key_guide_text(encryption_method, encryption_keys)
    
    # For Approach 2, include sample plaintext and encrypted version
    elif assistant_approach == "2":
        # Import locally to avoid circular imports
        sample_text = "This is an encrypted text."
        sample_encrypted = encrypt(sample_text, encryption_method, encryption_keys)
        return f"Sample: {sample_text} -> {sample_encrypted}"
    
    # For Approach 3, include distorted encryption information
    elif assistant_approach == "3":
        encryption_info = generate_text_key_guide_text(encryption_method, encryption_keys)
        
        if api_key is None:
            raise ValueError("API key is required for Approach 3 but was not provided")
            
        distorter = GeneticTextDistorter(api_key=api_key, min_unchanged_weight=min_unchanged_weight)
        print("Distorting encryption information...")
        results = distorter.train(encryption_info, generations=5)
        return results['text']['distorted_text']
    
    return ""