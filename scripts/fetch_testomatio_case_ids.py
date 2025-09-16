import requests

# Set these variables with your own credentials:
API_KEY = "tstmt_IzKNbISLsO9b5nRDbz3hdrbVOBV94NWuSA1757862769"         # e.g., 'fx6f57a866i9'
PROJECT_ID = "jokes-app-test"              # e.g., '123456'

BASE_URL = "https://api.testomat.io"
ENDPOINT = f"/projects/{PROJECT_ID}/test-cases"
HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

def fetch_case_ids():
    url = BASE_URL + ENDPOINT
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to fetch test cases:", response.status_code, response.text)
        return []

    cases = response.json()
    for case in cases:
        print(f"Name: {case.get('title', case.get('name'))} | ID: {case.get('id')}")

if __name__ == "__main__":
    fetch_case_ids()