import binascii
import random
from Crypto.Cipher import DES, ChaCha20, AES
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# Encryption functions
def caesar_encrypt(text, shift):
    result = ""
    
    for char in text:
        if char.isalpha():
            # Determine the ASCII offset (65 for uppercase, 97 for lowercase)
            ascii_offset = 65 if char.isupper() else 97
            
            # Apply the encryption formula: (position + shift) % 26
            encrypted_char = chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            result += encrypted_char
        else:
            # Keep non-alphabetic characters unchanged
            result += char    
    
    return result

def pad(text):
    while len(text) % 8 != 0:
        text += " "  # Padding with spaces
    return text

def des_encrypt(plain_text, key):
    cipher = DES.new(key, DES.MODE_ECB)  # Create DES cipher
    padded_text = pad(plain_text)  # Ensure text is a multiple of 8
    encrypted_bytes = cipher.encrypt(padded_text.encode())  # Encrypt text
    return binascii.hexlify(encrypted_bytes).decode()  # Convert to hex

def aes_encrypt(plainText, key, iv):    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Pad plaintext to be a multiple of AES block size (16 bytes)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_text = padder.update(plainText.encode()) + padder.finalize()
    
    cipher_text = encryptor.update(padded_text) + encryptor.finalize()
    return binascii.hexlify(iv + cipher_text).decode()

def chacha20_encrypt(plaintext, key, nonce):
    """Encrypts a message using ChaCha20 and returns a JSON string with nonce and ciphertext."""
    cipher = ChaCha20.new(key=key, nonce=nonce)
    ciphertext = cipher.encrypt(plaintext.encode())

    return binascii.hexlify(ciphertext).decode()

def encrypt(question, method, keys):
    """Encrypt a question using the specified method and keys"""
    if method == "1":  # Caesar
        return caesar_encrypt(question, keys["caesar"])
    elif method == "2":  # DES
        return des_encrypt(question, keys["des"])
    elif method == "3":  # AES
        return aes_encrypt(question, keys["aes"]["key"], keys["aes"]["iv"])
    elif method == "4":  # ChaCha20
        return chacha20_encrypt(question, keys["chacha20"]["key"], keys["chacha20"]["nonce"])
    else:
        return question  # No encryption
