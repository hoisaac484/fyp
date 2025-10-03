from modules.communication_module.communication_module import run_cli

# OpenAI API Key - typically this would be stored securely or passed as an environment variable
api_key = ""

if __name__ == "__main__":
    run_cli(api_key)