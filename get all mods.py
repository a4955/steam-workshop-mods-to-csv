import requests
import pandas as pd
import time
import os

API_KEY = '' # Must input your own Steam API Key
APP_ID = '311210' # Using COD Black Ops 3 app ID as an example
WORKSHOP_API_URL = "https://api.steampowered.com/IPublishedFileService/QueryFiles/v1/"
CSV_FILENAME = 'steam_workshop_mods.csv'

def fetch_workshop_items(page, app_id, api_key):
    params = {
        'key': api_key,
        'appid': app_id,
        'page': page,
        'page_size': 100,
        'return_details': True,
        'return_metadata': True
    }

    response = requests.get(WORKSHOP_API_URL, params=params)

    if response.status_code == 403:
        print("Access forbidden. Check your API key and permissions.")
        return None
    elif response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return None
    
    return response.json()

def save_mod_to_csv(mod_data, csv_filename, write_header=False):
    df = pd.DataFrame([mod_data])
    
    df.to_csv(csv_filename, mode='a', header=write_header, index=False)

def extract_and_save_mods_to_csv(app_id, api_key, csv_filename):
    all_mods = []
    page = 1
    total_results = 1
    
    file_exists = os.path.isfile(csv_filename)
    
    while total_results > 0:
        print(f"Fetching page {page}...")
        data = fetch_workshop_items(page, app_id, api_key)
        
        if data is None or 'response' not in data:
            break
        
        response_data = data['response']
        mods = response_data.get('publishedfiledetails', [])
        
        if not mods:
            print(f"No mods returned on page {page}. Stopping pagination.")
            break
        
        print(f"Fetched {len(mods)} mods on page {page}.")
        
        for mod in mods:
            mod_data = {
                'title': mod.get('title', 'N/A'),
                'publishedfileid': mod.get('publishedfileid', 'N/A'),
                'author_steam_id': mod.get('creator', 'N/A'),
                'file_url': mod.get('file_url', 'N/A'),
                'time_created': pd.to_datetime(mod.get('time_created', 'N/A'), unit='s', errors='coerce'),
                'time_updated': pd.to_datetime(mod.get('time_updated', 'N/A'), unit='s', errors='coerce'),
            }
            
            save_mod_to_csv(mod_data, csv_filename, write_header=not file_exists)
            file_exists = True

        page += 1
        time.sleep(1)  # Rate limiting

    print(f"Finished fetching mods. All mods saved to {csv_filename}.")

if __name__ == "__main__":
    extract_and_save_mods_to_csv(APP_ID, API_KEY, CSV_FILENAME)
