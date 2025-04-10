import requests

try:
    # Replace with the actual URL/port of your Ollama service
    response = requests.get("http://localhost:11434/status")
    if response.ok:
        print("Ollama is running!")
        print("Status info:", response.json())
    else:
        print("Ollama returned an error status:", response.status_code)
except requests.ConnectionError:
    print("Could not connect to Ollama. It may not be running.")
