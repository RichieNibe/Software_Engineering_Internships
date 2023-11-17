import requests
import re
from bs4 import BeautifulSoup
import os
import subprocess


def remove_emojis(text):

    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  
                               u"\U0001F300-\U0001F5FF"  
                               u"\U0001F680-\U0001F6FF"  
                               u"\U0001F1E0-\U0001F1FF"  
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def scrape_internships(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table')

    internships = []

    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            a_tag = cell.find('a')
            if a_tag and a_tag.has_attr('href'):
                url = a_tag['href']

                if 'simplify.jobs/c/' in url:
                    company_name = url.split('/')[-1]
                    row_data.append(company_name)
                else:
                    row_data.append(url)
            else:
                cell_text = remove_emojis(cell.get_text(strip=True))
                row_data.append(cell_text)

        if row_data:
            internships.append(row_data)

    return internships


def create_markdown_table(data):
    markdown = "| " + " | ".join(data[0]) + " |\n"  # headers
    markdown += "| " + " | ".join(["---"] * len(data[0])) + " |\n"  # separator
    for row in data[1:]:
        markdown += "| " + " | ".join(row) + " |\n"
    return markdown


URL = os.getenv('SCRAPER_URL')
scraped_data = scrape_internships(URL)

markdown_table = create_markdown_table(scraped_data)


with open('../Software-Engineering-Internships/README.md', 'w') as file:
    file.write(markdown_table)

subprocess.run(["git", "add", "README.md"])
subprocess.run(["git", "commit", "-m", "Updated dataset"])
subprocess.run(["git", "push"])
