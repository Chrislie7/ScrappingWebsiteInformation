import requests
from bs4 import BeautifulSoup
import re
import csv
import time


def extract_phone_number_from_text(text):
    # Regex to find phone numbers in the format XXX-XXX-XXXX
    match = re.search(r'\b(\d{3})[^\d]*(\d{3})[^\d]*(\d{4})\b', text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return 'No phone number'


def scrape_sub_link(link):
    # Fetch the sub-link page content
    response = requests.get(link)
    page_content = response.content

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')

    # Extract details from the sub-link
    title_element = soup.find('h1', {'class': 'title-4206718449'})
    description_element = soup.find(
        'div', {'class': 'descriptionContainer-2067035870'})
    # Get all text from the page for phone number extraction
    contact_info = soup.get_text().strip()

    g_txt = description_element.get_text(strip=False, separator=" ")
    phone_number = extract_phone_number_from_text(contact_info)
    email = extract_email_from_text(g_txt)
    # Extract phone number from the contact info text
    #
    # Print details
    title = title_element.text.strip() if title_element else 'No title'
    description = description_element.text.strip(
    ) if description_element else 'No description'

    return [title, phone_number, email, link]


def extract_email_from_text(text):

    # Regex pattern to find the email address and capture up to 3 words after '.com'
    pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com)\s*([^\.]*?)(?:\s+(\w+(?:\s+\w+){0,2}))?'

    # Find all matches in the text
    matches = re.findall(pattern, text)

    # Print the results
    for match in matches:
        email = match[0]
        following_text = match[2] if match[2] else ""
        return email

    # Regex to find email addresses
    match = re.search(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text)
    if match:
        return match.group(0)
    return 'No email address'
#


def extract_item_links(link):
    # URL of the Kijiji page
    url = "https://www.kijiji.ca/b-services/canada/c72l0"

    # Fetch the page content
    response = requests.get(url)
    page_content = response.content

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')
    # Find the unordered list containing the items
    ul_element = soup.find('ul', {'class': 'sc-bcb4ed5-0 bYINEN'})
    links = []
    if ul_element:
        # Iterate through each list item
        for li in ul_element.find_all('li'):
            # Skip if the item has the class 'top-ad'
            if 'top-ad' in li.get('class', []):
                continue

            # Extract title, description, and link
            title_element = li.find('a', {'class': 'sc-7c655743-0 ctMqFL'})
            description_element = li.find(
                'p', {'class': 'sc-e7aa8908-0 fDnAMm sc-7c655743-16 caCduP'})
            link_element = title_element.get('href') if title_element else None
            # Print details
            title = title_element.text.strip() if title_element else 'No title'
            description = description_element.text.strip(
            ) if description_element else 'No description'
            link = f"https://www.kijiji.ca{link_element}" if link_element else 'No link'
            # call function
            links.append(link)

            # print(f"Title: {title}")
            # print(f"Description: {description}")
            # print(f"Link: {link}")
            # print("="*40)
    else:
        print("No items found")

    return links


# Open CSV file for writing
with open('kijiji_listings.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow(['Title', 'Phone', 'Email', 'Link'])

    for page_number in range(1, 75):  # Adjust range as needed
        print(f"Scraping Page {page_number}")
        item_links = extract_item_links(page_number)
        for link in item_links:
            data = scrape_sub_link(link)
            writer.writerow(data)
