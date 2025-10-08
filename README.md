# Private Chat System with Large Language Models using Encrypted Text Interpretation by Artificial Intelligence

This project aims to help Large Language models (LLMs) interpret encrypted text to enhance
the security of communication between LLMs and users. A key challenge for this project is
that LLMs are not able to understand ciphertext directly. A framework that enables LLMs to
interpret encrypted queries without exposing plaintext information will be proposed. In this
project, we will investigate three different approaches: (1) passing the encryption key, method,
and encrypted text together, (2) providing a plaintext-ciphertext pair alongside the encrypted
query, and (3) distorting the encryption key and method using a Genetic Algorithm (GA).
These approaches will be tested using Caesar, DES, AES, and ChaCha20 encryption to
evaluate decryption success rates and response times. Results show that Approach 3 has the
best security-usability trade-off on average, although different distortion levels will affect the
performance of this approach. This research contributes a novel encrypted AI communication
framework that enhances privacy while preserving functionality.
