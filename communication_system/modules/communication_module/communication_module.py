import openai
from modules.instruction_module.instruction_module import (
    get_assistant_configs,
    generate_guide_text
)
from modules.communication_module.communication_encryptor import (
    ENCRYPTION_METHODS,
    encrypt_question,
    generate_encryption_keys
)

def setup_client(api_key):
    """Set up and return the OpenAI client"""
    return openai.OpenAI(api_key=api_key)

def get_or_create_assistant(client, assistant_config):
    """Get existing assistant or create a new one based on configuration"""
    assistants = client.beta.assistants.list()
    
    # Check if assistant already exists
    for a in assistants.data:
        if a.name == assistant_config["name"]:
            print(f"Using existing assistant: {assistant_config['name']}")
            return a
    
    # Create new assistant if it doesn't exist
    print(f"Creating new assistant: {assistant_config['name']}")
    return client.beta.assistants.create(
        name=assistant_config["name"],
        instructions=assistant_config["instructions"],
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}]
    )

def create_new_thread(client):
    """Create a new conversation thread"""
    return client.beta.threads.create()

def send_message_to_assistant(client, assistant, thread, message_content):
    """Send a message to the assistant and get the response"""
    # Add user message to thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message_content
    )
    
    # Start a run and wait for completion
    print(f"Processing...")
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
        
    # Check if the run is completed and return response
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")  # Ensure messages are retrieved in correct order

        assistant_responses = []
        for msg in messages.data:
            if msg.role == "assistant":
                # Extract text from all messages by assistant
                assistant_responses.append(msg.content[0].text.value)

        # Join all responses together to get the full output
        full_response = "\n".join(assistant_responses)
        return full_response

    else:
        return f"Run Status: {run.status}"

def encrypt_user_question(question, encryption_method, encryption_keys):
    """Encrypt a user question using the specified method and keys"""
    return encrypt_question(question, encryption_method, encryption_keys)

def run_cli(api_key):
    """Run the CLI in interactive mode"""
    client = setup_client(api_key)
    
    print("Welcome to the OpenAI Assistant CLI")
    print("==================================")
    
    current_assistant = None
    current_thread = None
    encryption_keys = None
    encryption_method = None
    min_unchanged_weight = None
    assistant_approach = None
    
    # Get configurations
    ASSISTANT_CONFIGS = get_assistant_configs()
    
    while True:
        # Reset session if needed
        if current_assistant is None:
            # First, select encryption method
            print("\nSelect encryption method:")
            for key, name in ENCRYPTION_METHODS.items():
                print(f"{key}. {name}")
            print("0. Exit")
            
            encryption_method = input("\nEnter your choice (0-4): ")
            
            if encryption_method == "0":
                print("Goodbye!")
                break
                
            while encryption_method not in ENCRYPTION_METHODS:
                print("Invalid choice. Please try again.")
                encryption_method = input("Enter your choice (1-4): ")
            
            print(f"Using {ENCRYPTION_METHODS[encryption_method]} for encryption")
            
            # Generate new encryption keys for this session
            encryption_keys = generate_encryption_keys()
            
            # Then select assistant
            print("\nSelect an assistant:")
            for key, config in ASSISTANT_CONFIGS.items():
                print(f"{key}. {config['name']}")
            print("0. Change encryption/Exit")
            
            choice = input("\nEnter your choice (0-3): ")
            
            if choice == "0":
                current_assistant = None
                current_thread = None
                encryption_keys = None
                encryption_method = None
                min_unchanged_weight = None
                assistant_approach = None
                continue
                
            if choice not in ASSISTANT_CONFIGS:
                print("Invalid choice. Please try again.")
                continue
            
            # Store assistant approach for later use
            assistant_approach = choice
                
            # Get or create the selected assistant
            assistant_config = ASSISTANT_CONFIGS[choice]
            current_assistant = get_or_create_assistant(client, assistant_config)
            
            # Create a new thread for this conversation
            current_thread = create_new_thread(client)
            
            print(f"\nNow chatting with: {assistant_config['name']}")
            
            # If using Approach 3, get the min_unchanged_weight
            if choice == "3":
                while True:
                    try:
                        min_unchanged_weight = float(input("\nEnter min_unchanged_weight value (0-100, default is 50.0): ") or "50.0")
                        if 0 <= min_unchanged_weight <= 100:
                            break
                        else:
                            print("Value must be between 0 and 100. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                print(f"Using min_unchanged_weight: {min_unchanged_weight}")
            
            print("Type 'reset' to change encryption/assistant or 'exit' to quit")
        
        # Get the question from the user
        question = input("\nEnter your question (or 'reset'/'exit'): ")
        
        # Check for special commands
        if question.lower() == 'exit':
            print("Goodbye!")
            break
        elif question.lower() == 'reset':
            current_assistant = None
            current_thread = None
            encryption_keys = None
            encryption_method = None
            min_unchanged_weight = None
            assistant_approach = None
            continue
            
        if not question:
            print("Question cannot be empty.")
            continue
        
        # Encrypt the question using the communication module
        encrypted_question = encrypt_user_question(question, encryption_method, encryption_keys)
        
        # Generate guide text using the instruction module
        guide_text = generate_guide_text(
            assistant_approach, 
            encryption_method, 
            encryption_keys,
            min_unchanged_weight,
            api_key  # Pass the API key to the instruction module
        )
            
        print("\nProcessing your request... This may take a moment.")
        print(f"Encrypted question: {encrypted_question}")
        
        # Prepare the user message
        user_message = f"{guide_text}\nEncrypted question: {encrypted_question}"
        print(user_message)
        
        # Process the question using the communication module
        response = send_message_to_assistant(client, current_assistant, current_thread, user_message)
        
        print("\nResponse:")
        print(response)
        
        print("\n" + "-" * 50)