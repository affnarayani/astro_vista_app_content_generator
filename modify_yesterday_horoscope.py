import json
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv(dotenv_path='.env', override=True)

# Configure the Gemini API with the key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in GitHub Secrets or .env file.")
genai.configure(api_key=api_key)

# Initialize the Gemini model with gemini-2.5-flash
model = genai.GenerativeModel('gemini-2.5-flash')

def rewrite_text(original_text, section_name, sign):
    """
    Use Gemini API to rewrite the given horoscope text
    Includes retry mechanism for API exceptions
    """
    prompt = f"""
    Rewrite the following {section_name} for {sign} in a more professional tone.
    Do not use any special characters or emojis.
    Write only the rewritten text without any additional explanation or headers.
    Write in simplest English language without using difficult words or jargon.
    Keep the length of the rewritten text similar to the original text.
    Make sure that the rewritten text is grammatically correct and coherent.
    The rewritten text should be suitable for publication on astrology websites.
    
    Original text: {original_text}
    
    Rewritten {section_name}:
    """
    
    max_retries = 3
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            response = model.generate_content(prompt)
            # Wait for 3 seconds between API calls to avoid rate limiting
            time.sleep(3)
            return response.text.strip()
        except Exception as e:
            retry_count += 1
            print(f"  Error during API call: {str(e)}")
            
            if retry_count > max_retries:
                print(f"  Maximum retries reached for {sign} - {section_name}. Skipping.")
                return original_text
            
            print(f"  Waiting 20 seconds before retry {retry_count}/{max_retries}...")
            time.sleep(20)
            print(f"  Retrying API call for {sign} - {section_name}...")

def main():
    # Read the original JSON file
    with open('yesterday_horoscope.json', 'r') as file:
        horoscope_data = json.load(file)
    
    # Process each zodiac sign
    for sign_data in horoscope_data['horoscopes']:
        sign = sign_data['sign']
        print(f"\nProcessing {sign} horoscope...")
        
        # Rewrite each section for the current sign
        sections = sign_data['sections']
        
        # Rewrite each section
        for section_name in sections:
            print(f"  Rewriting {section_name}...")
            original_text = sections[section_name]
            rewritten_text = rewrite_text(original_text, section_name, sign)
            sections[section_name] = rewritten_text
    
    # Save the modified data to a new file
    with open('modified_yesterday_horoscope.json', 'w') as file:
        json.dump(horoscope_data, file, indent=4)
    
    print("\nAll horoscopes successfully modified and saved to 'modified_yesterday_horoscope.json'")

if __name__ == "__main__":
    main()