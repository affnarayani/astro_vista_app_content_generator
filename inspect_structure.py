import requests
from bs4 import BeautifulSoup
import sys

def inspect_page():
    # Set console to handle UTF-8
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    url = 'https://www.prokerala.com/astrology/yearly-horoscope/aries.html'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the h1 tag
    h1_tag = soup.find('h1')
    if h1_tag:
        print(f"H1 tag found: {h1_tag.text.strip()}")
    else:
        print("No h1 tag found")
    
    # Find the article tag
    article = soup.find('article')
    if not article:
        print("No article tag found")
        return
    
    print("Article tag found")
    
    # Find all p tags within the article
    p_tags = article.find_all('p')
    print(f"Found {len(p_tags)} p tags in article")
    
    # Print the first few p tags
    for i, p in enumerate(p_tags[:5]):
        has_link = p.find('a') is not None
        print(f"P tag {i+1} has link: {has_link}")
        try:
            print(f"P tag {i+1} text preview: {p.text.strip()[:50]}")
        except UnicodeEncodeError:
            print(f"P tag {i+1} contains special characters that can't be displayed")
    
    # Find all divs with class 'horoscope-panel'
    panels = article.find_all('div', class_='horoscope-panel')
    print(f"Found {len(panels)} horoscope-panel divs")
    
    # Check for any other relevant elements
    sections = article.find_all('section')
    print(f"Found {len(sections)} section tags")
    
    divs = article.find_all('div')
    print(f"Found {len(divs)} div tags")
    
    # Check for any classes on p tags
    p_classes = set()
    for p in p_tags:
        if p.get('class'):
            p_classes.add(' '.join(p.get('class')))
    
    if p_classes:
        print(f"Found p tags with these classes: {', '.join(p_classes)}")
    else:
        print("No p tags with classes found")
    
    # Check for any h2 or h3 tags that might indicate sections
    h2_tags = article.find_all('h2')
    print(f"Found {len(h2_tags)} h2 tags")
    if h2_tags:
        for i, h2 in enumerate(h2_tags[:3]):
            print(f"H2 tag {i+1} text: {h2.text.strip()}")
    
    h3_tags = article.find_all('h3')
    print(f"Found {len(h3_tags)} h3 tags")
    if h3_tags:
        for i, h3 in enumerate(h3_tags[:3]):
            print(f"H3 tag {i+1} text: {h3.text.strip()}")

if __name__ == "__main__":
    inspect_page()