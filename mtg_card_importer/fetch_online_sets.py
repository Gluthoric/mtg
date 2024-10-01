import requests
import json

# Scryfall API endpoint to get all sets
SCRYFALL_SETS_URL = "https://api.scryfall.com/sets"

# Output file to store the online-only sets
OUTPUT_FILE = 'online_sets.json'

def fetch_scryfall_sets():
    """Fetches all Magic: The Gathering sets from the Scryfall API."""
    try:
        response = requests.get(SCRYFALL_SETS_URL)
        response.raise_for_status()  # Raise error for bad status codes
        data = response.json()
        return data['data']  # Extract 'data' field from the response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Scryfall API: {e}")
        return []

def filter_online_only_sets(sets):
    """Filters sets that are online-only (digital)."""
    online_only_sets = [set_info['code'] for set_info in sets if set_info.get('digital', False)]
    return online_only_sets

def save_to_file(data, file_path):
    """Saves the filtered set codes to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Online-only set codes saved to {file_path}")
    except IOError as e:
        print(f"Error saving file: {e}")

def main():
    print("Fetching all sets from Scryfall...")
    sets = fetch_scryfall_sets()

    if sets:
        print(f"Total sets fetched: {len(sets)}")
        online_only_sets = filter_online_only_sets(sets)
        print(f"Found {len(online_only_sets)} online-only sets.")

        # Save the online-only sets to a file
        save_to_file(online_only_sets, OUTPUT_FILE)
    else:
        print("No sets fetched.")

if __name__ == "__main__":
    main()
