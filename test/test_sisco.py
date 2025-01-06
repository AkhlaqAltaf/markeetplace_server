import requests

# Siscomex API configuration
API_BASE_URL = "https://api.siscomex.gov.br"  # Replace with the actual base URL
API_KEY = "your_api_key_here"  # Replace with your actual API key


# Function to search NCM by keyword
def search_ncm_by_keyword(keyword):
    endpoint = f"{API_BASE_URL}/ncm/search"
    params = {"keyword": keyword}
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(endpoint, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


# Function to retrieve detailed attributes of a specific NCM code
def get_ncm_details(ncm_code):
    endpoint = f"{API_BASE_URL}/ncm/{ncm_code}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


# Example usage
if __name__ == "__main__":
    # Search NCM by keyword
    keyword = "fertilizers"
    search_results = search_ncm_by_keyword(keyword)
    if search_results:
        print("Search Results:", search_results)

    # Get details of a specific NCM code
    ncm_code = "31821018"
    ncm_details = get_ncm_details(ncm_code)
    if ncm_details:
        print("NCM Details:", ncm_details)
