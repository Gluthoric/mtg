import re
from bs4 import BeautifulSoup

def parse_scryfall_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # Find all card grid items
    card_items = soup.find_all('div', class_='card-grid-item')

    # Remove all card grid items from the soup
    for item in card_items:
        item.decompose()

    # Get the remaining HTML content
    non_card_elements = str(soup)

    return non_card_elements

def main():
    file_path = '/home/gluth/mtg/Scryfall_Grouping.html'
    non_card_content = parse_scryfall_html(file_path)

    # Write the non-card content to a new file
    output_file = 'non_card_elements.html'
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(non_card_content)

    print(f"Non-card elements have been extracted and saved to {output_file}")

if __name__ == "__main__":
    main()