import secrets
import toml

def generate_api_key(client_name: str, secrets_file: str = "secrets.toml"):
    """
    Generates a strong API key, saves it in secrets.toml, and updates it if the client_name already exists.
    
    Args:
        client_name (str): The name of the client for whom the API key is being generated.
        secrets_file (str): The path to the secrets.toml file. Default is "secrets.toml".
        
    Returns:
        str: The generated API key.
    """
    # Generate a strong API key
    api_key = secrets.token_urlsafe(32)  # 32-byte key
    
    # Load existing secrets from the file, if it exists
    try:
        secrets_data = toml.load(secrets_file)
    except FileNotFoundError:
        secrets_data = {}
    
    # Update or add the API key for the client
    secrets_data[client_name] = api_key
    
    # Save the updated secrets back to the file
    with open(secrets_file, "w") as f:
        toml.dump(secrets_data, f)
    
    print(f"API key for '{client_name}' generated and saved in {secrets_file}.")
    return api_key

# Example usage
if __name__ == "__main__":
    client_name = "property_friends"
    api_key = generate_api_key(client_name)
    print(f"Generated API Key: {api_key}")
