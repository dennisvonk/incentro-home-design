import google.genai as genai

# Initialize client with your API key
client = genai.Client(api_key="AIzaSyBr5ybCr2XQ_l-qQYOhyRlg7cUiATyoXOQ")

# List all available models
print("Available models with supported actions:\n")
for model in client.models.list():
    print(f"Model: {model.name}")
    print(f"  Display name: {model.display_name}")
    print(f"  Supported actions: {model.supported_actions}")
    print()
