import os
import requests

ragflow_base_url = os.getenv("RAGFLOW_BASE_URL", "https://demo.ragflow.io/v1/api")
ragflow_api_key = os.getenv("RAGFLOW_API_KEY", "")

def upload_file_to_kb(file_path, kb_name):
    if not ragflow_api_key:
        raise RuntimeError("RAGFLOW_API_KEY is not configured")
    headers = {
        "Authorization": f"Bearer {ragflow_api_key}"
    }
    
    files = {
        'file': open(file_path, 'rb')
    }
    data = {
        "kb_name": kb_name,
        "run": "1",
        "parser_id": "naive"
    }
    
    response = requests.post(f"{ragflow_base_url}/document/upload", headers=headers, files=files, data=data, proxies={"http": None, "https": None})
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

# Function to upload all files in a directory
def upload_all_files(directory, kb_name):
    for file_name in os.listdir(directory):
        if file_name.endswith('.pdf'):  # Only process PDF files
            file_path = os.path.join(directory, file_name)
            print(f"Uploading file: {file_path}")
            response = upload_file_to_kb(file_path, kb_name)
            print(response)

# Specify the directory containing the split PDF files and the knowledge base name
directory = "./知识库"  # Update this path to your directory containing the split files
kb_name = "犬科"

# Call the function to upload all files
upload_all_files(directory, kb_name)
