import csv
import time
import random
from bs4 import BeautifulSoup
import requests


def fetch_html(url, retries=3, delay=10):
    """
    Fetch the HTML content of the given URL with retries and delay.
    """
    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            time.sleep(delay * (attempt + 1))
    return None


def parse_containers(html, tag, class_name=None):
    """
    Parse the HTML to extract containers with the specified class.
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all(tag, class_=class_name)


def extract_commander(container):
    """
    Extract the commander name from the container.
    """
    commander_tag = container.find('a', class_="card-link card-hover")
    return commander_tag.get_text(strip=True) if commander_tag else None


def extract_decks(container):
    """
    Extract deck names and URLs from the container.
    """
    ul_tag = container.find('ul')
    decks = []
    if ul_tag:
        for li_tag in ul_tag.find_all('li'):
            a_tag = li_tag.find('a')
            if a_tag:
                deck_name = a_tag.get_text(strip=True)
                deck_url = 'https://tappedout.net' + a_tag['href']
                decks.append((deck_name, deck_url))
    return decks


def extract_cards(container):
    """
    Extract cards and their quantities from the container.
    """
    cards = []
    li_tags = container.find_all('li', class_='member')
    if li_tags:
        for li_tag in li_tags:
            a_tags = li_tag.find_all('a')
            if len(a_tags) >= 2:
                number_of_cards = a_tags[0].get_text(strip=True)[:-1]
                card = a_tags[1].get_text(strip=True)
                cards.append((card, number_of_cards))
    return cards


def save_to_csv(data, output_file):
    """
    Save the extracted data to a CSV file.
    """
    print("Saving data to CSV...")
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Commander", "Deck Name", "Card", "Number of Cards"])
        for row in data:
            if all(row):  # Skip rows with None values
                writer.writerow(row)
    print(f"Data successfully written to {output_file}")


def main(url, output_file):
    """
    Main function to orchestrate the scraping and saving.
    """
    html = fetch_html(url)
    if not html:
        print("Failed to fetch the main URL.")
        return

    containers = parse_containers(html, 'div', 'panel-body')
    extracted_data = []
    processed_commanders = 0
    total_commanders = len(containers)

    for container in containers:
        commander = extract_commander(container)
        if not commander:
            continue

        decks = extract_decks(container)
        if not decks:
            extracted_data.append([commander, None, None, None])
            continue

        for (deck_name, deck_url) in decks:
            if not deck_url:
                extracted_data.append([commander, deck_name, None, None])
                continue

            html = fetch_html(deck_url)

            if html:
                card_containers = parse_containers(html, 'ul', 'boardlist')
                for card_container in card_containers:
                    cards = extract_cards(card_container)
                    for (card, number_of_cards) in cards:
                        extracted_data.append([commander, deck_name, card, number_of_cards])
            else:
                extracted_data.append([commander, deck_name, None, None])

            time.sleep(random.uniform(1, 3))

        processed_commanders += 1
        print(f"Processed {processed_commanders} commanders out of {total_commanders} commanders.")

    save_to_csv(extracted_data, output_file)
    print(f"Data successfully written to {output_file}")


if __name__ == "__main__":
    url = 'https://tappedout.net/mtg-decks/pauper-edh-deck-compendium/'
    output_file = 'commanders_and_decks.csv'
    main(url, output_file)
