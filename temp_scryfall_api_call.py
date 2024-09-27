import requests
import json

def get_enduring_innocence_cards():
    url = "https://api.scryfall.com/cards/search"
    params = {
        "q": "!\"Enduring Innocence\" set:dsk",
        "unique": "prints",
        "order": "released",
        "dir": "asc"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        cards = data.get('data', [])

        # Pretty print the JSON output
        print(json.dumps(cards, indent=2))

        # Optionally, save to a file
        with open('enduring_innocence_cards.json', 'w') as f:
            json.dump(cards, f, indent=2)

        print(f"Found {len(cards)} versions of Enduring Innocence")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    get_enduring_innocence_cards()