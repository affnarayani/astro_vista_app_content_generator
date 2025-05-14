import requests
from bs4 import BeautifulSoup
import json
import re
import time

def get_weekly_horoscope(zodiac_sign):
    """
    Fetch weekly horoscope for the given zodiac sign from ProKerala website.
    Implements retry mechanism.
    
    Args:
        zodiac_sign (str): Name of the zodiac sign (e.g., 'aries', 'taurus', etc.)
        
    Returns:
        tuple: A tuple containing:
            - dict: A dictionary with the sign, title, and content
            - BeautifulSoup: The soup object of the page

    Raises:
        Exception: If all retry attempts fail, an exception is raised to fail the script
    """
    # Ensure zodiac sign is lowercase for the URL
    zodiac_sign = zodiac_sign.lower()
    
    # Construct the URL
    url = f"https://www.prokerala.com/astrology/weekly-horoscope/{zodiac_sign}.html"
    
    # Initialize result dictionary
    result = {
        'sign': zodiac_sign.capitalize(),
        'title': '',
        'content': []
    }

    # Define headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    # Send HTTP request with unlimited retries
    attempt = 1
    max_attempts = 3
    success = False
    
    while attempt <= max_attempts:
        try:
            print(f"Attempt {attempt} for {zodiac_sign}...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            success = True
            break  # Exit the loop if request is successful
        except requests.exceptions.RequestException as e:
            print(f"Error fetching horoscope for {zodiac_sign} (Attempt {attempt}): {e}")
            if attempt < max_attempts:
                print(f"Retrying in 30 seconds...")
                time.sleep(30)  # Wait for 30 second before retrying
            else:
                print(f"All {max_attempts} attempts failed for {zodiac_sign}.")
            attempt += 1
    
    # Check if all attempts were exhausted
    if not success:
        raise Exception(f"Failed to fetch horoscope for {zodiac_sign}")
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get the title from h1 tag
    h1_tag = soup.find('h1')
    if h1_tag:
        result['title'] = h1_tag.text.strip()
    
    # Find the article tag which contains the horoscope content
    article = soup.find('article')
    if article:
        # Find all p tags within the article
        p_tags = article.find_all('p')
        
        # Process each p tag
        for p in p_tags:
            # Skip p tags that contain links
            if p.find('a'):
                continue
            
            # Add the paragraph text to content
            paragraph_text = p.text.strip()
            if paragraph_text:
                result['content'].append(paragraph_text)
    
    return result, soup

def main():
    # List of all zodiac signs
    zodiac_signs = [
        "aries", "taurus", "gemini", "cancer", 
        "leo", "virgo", "libra", "scorpio", 
        "sagittarius", "capricorn", "aquarius", "pisces"
    ]
    
    # Initialize the final JSON structure
    horoscope_json = {
        "horoscopes": []
    }
    
    # Fetch horoscope for each zodiac sign
    for i, sign in enumerate(zodiac_signs):
        print(f"Fetching horoscope for {sign.capitalize()}...")
        horoscope_data, _ = get_weekly_horoscope(sign)
        horoscope_json["horoscopes"].append(horoscope_data)
        
        # Add a 3-second delay between requests (except after the last one)
        if i < len(zodiac_signs) - 1:
            print(f"Waiting 3 seconds before next request...")
            time.sleep(3)
    
    # Save to JSON file
    with open('weekly_horoscope.json', 'w', encoding='utf-8') as f:
        json.dump(horoscope_json, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()