import csv
from bs4 import BeautifulSoup
import requests


def fetch_html(url):
    """
    Fetch the HTML content of the given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"HTTP error occurred: {e}")
        return None


def parse_containers(html):
    """
    Parse the HTML to extract containers with the specified class.
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('div', class_="panel-body")


def extract_deck(container):
    """
    Extract the deck name from the container.
    """
    deck_tag = container.find('a', class_="card-link card-hover")
    return deck_tag.get_text(strip=True) if deck_tag else None


def extract_cards(container):
    """
    Extract cards and their URLs from the container.
    """
    ul_tag = container.find('ul')  # Find the unordered list containing cards
    cards = []
    if ul_tag:
        li_tags = ul_tag.find_all('li')  # Find all list items
        for li_tag in li_tags:
            a_tag = li_tag.find('a')  # Find the first <a> tag within the list item
            if a_tag:
                card = a_tag.get_text(strip=True)  # Text of the card
                card_url = 'https://tappedout.net' + a_tag['href']  # URL of the card
                cards.append((card, card_url))
    return cards


def save_to_csv(data, output_file):
    """
    Save the extracted data to a CSV file.
    """
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Decks", "Cards", "Cards URL"])
        for row in data:
            writer.writerow(row)


def main(url, output_file):
    """
    Main function to fetch, parse, and save data.
    """
    html = fetch_html(url)
    if not html:
        return

    containers = parse_containers(html)
    extracted_data = []

    for container in containers:
        deck = extract_deck(container)
        if not deck:
            continue

        cards = extract_cards(container)
        if cards:
            for card, card_url in cards:
                extracted_data.append([deck, card, card_url])
        else:
            extracted_data.append([deck, None, None])

    save_to_csv(extracted_data, output_file)
    print(f"Data successfully written to {output_file}")

if __name__ == '__mani__':
    url = 'https://tappedout.net/mtg-decks/pauper-edh-deck-compendium/'
    output_file = 'decks_and_cards.csv'
    main(url, output_file)
