import os
import requests

# Define directories for raw data
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(RAW_DATA_DIR, exist_ok=True)

def download_file(url, filename):
    """Download a file from a URL and save it to the raw data directory."""
    file_path = os.path.join(RAW_DATA_DIR, filename)
    if os.path.exists(file_path):
        print(f"{filename} already exists. Skipping download.")
        return file_path
    print(f"Downloading {filename} from {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded and saved to {file_path}")
    else:
        print(f"Failed to download {filename}. HTTP status code: {response.status_code}")
    return file_path

def extract_json(url, filename):
    """Extract JSON data from an API endpoint and save it."""
    file_path = os.path.join(RAW_DATA_DIR, filename)
    if os.path.exists(file_path):
        print(f"{filename} already exists. Skipping extraction.")
        return file_path
    print(f"Extracting JSON data from {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Extracted JSON data saved to {file_path}")
    else:
        print(f"Failed to extract JSON data. HTTP status code: {response.status_code}")
    return file_path

def main():
    # Dataset 1: akris.csv (accreditation courses)
    akris_url = "https://data.mpsv.cz/documents/1749923/7049685/akris.csv"
    download_file(akris_url, "akris.csv")
    
    
    # Dataset 3: rpss.json via API call
    rpss_url = "https://data.mpsv.cz/od/soubory/rpss/rpss.json"
    extract_json(rpss_url, "rpss.json")

if __name__ == "__main__":
    main()
