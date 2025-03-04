import requests
from bs4 import BeautifulSoup
import string
import re

# URL patterns
ARTIST_LIST_URL = "https://www.kissthisguy.com/{}-artists.htm"  # e.g., A-artists.htm, B-artists.htm, etc.
ARTIST_BASE_URL = "https://www.kissthisguy.com/"               # Base URL for relative links
API_URL = "https://misheard-melodies-api.onrender.com/lyrics"  # Your API endpoint

def extract_artist(soup, song_url):
    """
    Extract the artist's name from the page.
    First, try to find a dedicated element containing 'Artist:'.
    Otherwise, fall back to a regex search on the full text.
    """
    # Option 1: Look for an element (e.g., h1, h2, or p) that contains "Artist:"
    artist_element = soup.find(lambda tag: tag.name in ['h1', 'h2', 'p'] and "Artist:" in tag.get_text())
    if artist_element:
        text = artist_element.get_text()
        match = re.search(r"Artist:\s*(.+)", text)
        if match:
            return match.group(1).split('\n')[0].strip()
    
    # Option 2: Fallback: search the full text of the page
    page_text = soup.get_text()
    match = re.search(r"Artist:\s*(.+)", page_text)
    if match:
        return match.group(1).split('\n')[0].strip()
    
    return "Unknown Artist"

def scrape_song_page(song_url):
    print(f"Scraping song page: {song_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(song_url, headers=headers)
    except Exception as e:
        print(f"Exception fetching {song_url}: {e}")
        return

    if response.status_code != 200:
        print(f"❌ Error fetching {song_url} (status code {response.status_code})")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Attempt to extract the song title from an <h1> or from the <title> tag
    song_title = "Unknown Song"
    h1_tag = soup.find('h1')
    if h1_tag:
        song_title = h1_tag.get_text(strip=True)
    elif soup.title:
        song_title = soup.title.get_text(strip=True)
    
    # Extract the artist using our helper function
    artist = extract_artist(soup, song_url)
    
    # Extract misheard lyric links.
    # We assume misheard lyrics are in <a> tags that have a title attribute.
    misheard_links = soup.find_all('a', title=True)
    if not misheard_links:
        print(f"No misheard lyric links found on {song_url}")
        return

    for link in misheard_links:
        try:
            misheard = link.get_text(strip=True)
            original = link['title'].strip()  # The title attribute holds the original lyric info
            lyric_data = {
                "song_title": song_title,
                "artist": artist,
                "misheard": misheard,
                "original": original
            }
            print("Extracted lyric data:", lyric_data)
            response_post = requests.post(API_URL, json=lyric_data)
            if response_post.status_code == 201:
                print(f"✅ Added: {song_title} - {artist}")
            else:
                print(f"⚠️ Failed to add: {song_title} - {artist} (Status: {response_post.status_code})")
        except Exception as e:
            print(f"Exception processing a link on {song_url}: {e}")
            continue

def scrape_artist_pages():
    """
    Loop through artist listing pages (A–Z) and find song page links,
    then scrape each song page.
    """
    for letter in string.ascii_uppercase:  # Loop through A–Z
        url = ARTIST_LIST_URL.format(letter)
        print(f"\nScraping artist list page: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            print(f"Exception fetching {url}: {e}")
            continue

        if response.status_code != 200:
            print(f"❌ Error fetching {url} (status code {response.status_code})")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all <a> tags on the artist list page.
        links = soup.find_all('a', href=True)
        print(f"Found {len(links)} links on {url}")
        for link in links:
            href = link['href']
            # Check if the link is a song page by looking for "misheard" in the URL.
            if "misheard" in href.lower():
                full_url = ARTIST_BASE_URL + href
                print(f"Found song page link: {full_url}")
                scrape_song_page(full_url)

if __name__ == '__main__':
    scrape_artist_pages()


          


