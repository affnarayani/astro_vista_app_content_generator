import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import time

def extract_date_from_title(soup):
    """
    Extract the date from the h1 title on the webpage.
    
    Args:
        soup (BeautifulSoup): BeautifulSoup object of the webpage
        
    Returns:
        str: Date in ddmmyyyy format extracted from the title or None if extraction fails
    """
    # Find the h1 tag
    h1_tag = soup.find('h1')
    if not h1_tag:
        print("Warning: Could not find h1 tag on the page")
        return None
    
    # Extract the title text
    title_text = h1_tag.text.strip()
    print(f"Found title: {title_text}")
    
    # Extract the date part using regex
    # Example: "Today's Leo Horoscope - Monday, May 12, 2025"
    date_pattern = r'[A-Za-z]+, ([A-Za-z]+) (\d+), (\d{4})'
    match = re.search(date_pattern, title_text)
    
    if match:
        month_name, day, year = match.groups()
        
        # Convert month name to number
        month_dict = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }
        
        # If month name is not in dictionary, return None
        if month_name not in month_dict:
            print(f"Warning: Unknown month name: {month_name}")
            return None
            
        month = month_dict[month_name]
        
        # Format day with leading zero if needed
        day = day.zfill(2)
        
        # Combine into ddmmyyyy format
        formatted_date = f"{day}{month}{year}"
        print(f"Extracted date: {formatted_date}")
        return formatted_date
    else:
        print(f"Warning: Could not extract date from title: {title_text}")
        return None

def get_horoscope(zodiac_sign):
    """
    Fetch horoscope for the given zodiac sign from ProKerala website.
    Implements retry mechanism.
    
    Args:
        zodiac_sign (str): Name of the zodiac sign (e.g., 'aries', 'taurus', etc.)
        
    Returns:
        tuple: A tuple containing:
            - dict: A dictionary with the sign and sections with headings and content
            - BeautifulSoup: The soup object of the page

    Raises:
        Exception: If all retry attempts fail, an exception is raised to fail the script
    """
    # Ensure zodiac sign is lowercase for the URL
    zodiac_sign = zodiac_sign.lower()
    
    # Construct the URL
    base_url = f"https://www.prokerala.com/astrology/horoscope/?sign={zodiac_sign}&day=today"
    
    # Initialize result dictionary
    result = {
        'sign': zodiac_sign.capitalize(),
        'sections': {}
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
            response = requests.get(base_url, headers=headers, timeout=30)
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
    
    # Find the article tag which contains the horoscope content
    article = soup.find('article')
    if article:
        # Find all h2 tags within the article
        h2_tags = article.find_all('h2')
        
        # Find all horoscope-panel divs
        panels = article.find_all('div', class_='horoscope-panel')
        
        # Process each h2 tag and its corresponding panel
        for i, h2 in enumerate(h2_tags):
            if i < len(panels):  # Make sure we have a corresponding panel
                heading = h2.text.strip()
                
                # Get all paragraphs from the corresponding panel without a class
                p_tags = panels[i].find_all('p')
                content = ""
                for p in p_tags:
                    if not p.get('class'):  # Only include p tags without a class
                        content += p.text.strip()
                
                # Add to sections dictionary
                if content:
                    result['sections'][heading] = content
    
    return result, soup

def main():
    # List of all zodiac signs
    zodiac_signs = [
        "aries", "taurus", "gemini", "cancer", 
        "leo", "virgo", "libra", "scorpio", 
        "sagittarius", "capricorn", "aquarius", "pisces"
    ]
    
    # Variable to store the extracted date
    extracted_date = None
    
    # Initialize the final JSON structure
    horoscope_json = {
        "date": "",  # Will be updated with the extracted date
        "horoscopes": []
    }
    
    # Fetch horoscope for each zodiac sign
    for i, sign in enumerate(zodiac_signs):
        print(f"Fetching horoscope for {sign.capitalize()}...")
        horoscope_data, soup = get_horoscope(sign)
        horoscope_json["horoscopes"].append(horoscope_data)
        
        # Extract date from the first successful request
        if soup and extracted_date is None:
            extracted_date = extract_date_from_title(soup)
            if extracted_date is None:
                print("Failed to extract date from the page")
                return  # Exit if date extraction fails
        
        # Add a 3-second delay between requests (except after the last one)
        if i < len(zodiac_signs) - 1:
            print(f"Waiting 3 seconds before next request...")
            time.sleep(3)
    
    # Update the date in the JSON structure
    if extracted_date:
        horoscope_json["date"] = extracted_date
        
        # Save to JSON file
        with open('today_horoscope.json', 'w', encoding='utf-8') as f:
            json.dump(horoscope_json, f, indent=4, ensure_ascii=False)
        
        print(f"\nHoroscope data for date {extracted_date} has been saved to today_horoscope.json")
    else:
        print("Error: Could not extract date from any horoscope page. No data saved.")

if __name__ == "__main__":
    main()