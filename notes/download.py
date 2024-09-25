import requests

# URL for the default bulk data from Scryfall
SCRYFALL_BULK_DATA_URL = "https://api.scryfall.com/bulk-data"

def download_bulk_data():
    response = requests.get(SCRYFALL_BULK_DATA_URL)
    if response.status_code == 200:
        bulk_data_list = response.json().get('data', [])
        for data_item in bulk_data_list:
            if data_item.get('type') == 'default_cards':
                download_url = data_item.get('download_uri')
                print(f"Downloading data from: {download_url}")
                card_data_response = requests.get(download_url)
                if card_data_response.status_code == 200:
                    with open('scryfall_default_cards.json', 'wb') as f:
                        f.write(card_data_response.content)
                    print("Download complete!")
                else:
                    print("Failed to download card data.")
    else:
        print("Failed to fetch bulk data information.")

download_bulk_data()
